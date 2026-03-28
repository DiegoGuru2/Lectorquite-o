from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status
from sqlalchemy.orm import Session
from sqlalchemy import select, func, or_
from typing import List, Optional

from app.database import get_db
from app.models.lexicon import Word, Category, QuizQuestion, Comment, Vote, User
from app.schemas.lexicon import (
    WordResponse, WordPaged, WordCreate, WordUpdate,
    QuizQuestionResponse, CommentResponse, CommentCreate, 
    VoteResponse, CategoryResponse, CategoryCreate
)
from app.core.security import get_current_user, ensure_db_user, require_admin, UserAuthToken
from app.core.cloudinary_service import CloudinaryService

router = APIRouter()

# --- 1. CATEGORIAS ---

@router.get("/categories", response_model=List[CategoryResponse], summary="Listar Categorias")
def list_categories(db: Session = Depends(get_db)):
    return db.scalars(select(Category).order_by(Category.name.asc())).all()

@router.post("/categories", response_model=CategoryResponse, summary="Crear Categoria (Admin)")
def create_category(
    cat_in: CategoryCreate, 
    db: Session = Depends(get_db),
    current_user: UserAuthToken = Depends(require_admin)
):
    existing = db.scalar(select(Category).where(Category.name == cat_in.name))
    if existing:
        raise HTTPException(status_code=400, detail="Categoria ya existe")
    
    new_cat = Category(name=cat_in.name, description=cat_in.description)
    db.add(new_cat)
    db.commit()
    db.refresh(new_cat)
    return new_cat

# --- 2. LEXICO (Palabras) ---

@router.get("/words", response_model=WordPaged, summary="Listar palabras quitof (Paginado)")
def list_words(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = select(Word).where(Word.is_active == True)
    if search:
        query = query.where(or_(Word.term.ilike(f"%{search}%"), Word.meaning.ilike(f"%{search}%")))
    
    total = db.scalar(select(func.count()).select_from(query.subquery()))
    words = db.scalars(query.offset(skip).limit(limit)).all()
    
    results = []
    for w in words:
        item = WordResponse.model_validate(w)
        item.vote_count = len(w.votes)
        item.comment_count = len(w.comments)
        results.append(item)

    return {"total": total, "page": (skip // limit) + 1, "size": limit, "items": results}

@router.post("/words", response_model=WordResponse, summary="Proponer Nueva Palabra")
def propose_word(
    word_in: WordCreate,
    db: Session = Depends(get_db),
    current_user: UserAuthToken = Depends(ensure_db_user)
):
    existing = db.scalar(select(Word).where(Word.slug == word_in.slug))
    if existing:
        raise HTTPException(status_code=400, detail="El slug ya esta en uso")
    
    new_word = Word(
        term=word_in.term,
        slug=word_in.slug,
        meaning=word_in.meaning,
        origin=word_in.origin,
        is_active=False
    )
    
    if word_in.category_ids:
        categories = db.scalars(select(Category).where(Category.id.in_(word_in.category_ids))).all()
        new_word.categories = list(categories)

    db.add(new_word)
    db.commit()
    db.refresh(new_word)
    
    item = WordResponse.model_validate(new_word)
    item.vote_count = 0
    item.comment_count = 0
    return item

@router.put("/words/{slug}", response_model=WordResponse, summary="Actualizar Palabra (Admin)")
def update_word(
    slug: str,
    word_update: WordUpdate,
    db: Session = Depends(get_db),
    current_user: UserAuthToken = Depends(require_admin)
):
    word = db.scalar(select(Word).where(Word.slug == slug))
    if not word:
        raise HTTPException(status_code=404, detail="No encontrada")
    
    if word_update.meaning is not None:
        word.meaning = word_update.meaning
    if word_update.origin is not None:
        word.origin = word_update.origin
    if word_update.is_active is not None:
        word.is_active = word_update.is_active
    if word_update.is_featured is not None:
        word.is_featured = word_update.is_featured
    
    if word_update.category_ids is not None:
        categories = db.scalars(select(Category).where(Category.id.in_(word_update.category_ids))).all()
        word.categories = list(categories)

    db.commit()
    db.refresh(word)
    item = WordResponse.model_validate(word)
    item.vote_count = len(word.votes)
    item.comment_count = len(word.comments)
    return item

@router.delete("/words/{slug}", summary="Eliminar Palabra (Admin)")
def delete_word(
    slug: str,
    db: Session = Depends(get_db),
    current_user: UserAuthToken = Depends(require_admin)
):
    word = db.scalar(select(Word).where(Word.slug == slug))
    if not word:
        raise HTTPException(status_code=404, detail="No encontrada")
    
    db.delete(word)
    db.commit()
    return {"status": "success", "message": f"Palabra {slug} eliminada"}

@router.get("/words/featured", response_model=WordResponse, summary="La Palabra del Dia")
def get_featured_word(db: Session = Depends(get_db)):
    word = db.scalar(select(Word).where(Word.is_featured == True, Word.is_active == True))
    if not word:
        word = db.scalar(select(Word).where(Word.is_active == True).order_by(Word.created_at.desc()))
    
    if not word:
        raise HTTPException(status_code=404, detail="Aun no hay palabras veci")
    
    item = WordResponse.model_validate(word)
    item.vote_count = len(word.votes)
    item.comment_count = len(word.comments)
    return item

@router.get("/words/{slug}", response_model=WordResponse, summary="Ver palabra por su Slug (SEO)")
def get_word_by_slug(slug: str, db: Session = Depends(get_db)):
    word = db.scalar(select(Word).where(Word.slug == slug, Word.is_active == True))
    if not word:
        raise HTTPException(status_code=404, detail="Palabra no encontrada veci")
    
    item = WordResponse.model_validate(word)
    item.vote_count = len(word.votes)
    item.comment_count = len(word.comments)
    return item

# --- 3. INTERACCION (Social Warrior) ---

@router.post("/words/{slug}/vote", response_model=VoteResponse, summary="Votar (Q'cho o Batracio)")
def vote_word(
    slug: str,
    value: int = Query(..., ge=-1, le=1),
    db: Session = Depends(get_db),
    current_user: UserAuthToken = Depends(ensure_db_user)
):
    word = db.scalar(select(Word).where(Word.slug == slug))
    if not word:
        raise HTTPException(status_code=404, detail="Palabra no encontrada")
    
    existing = db.scalar(select(Vote).where(Vote.word_id == word.id, Vote.user_id == current_user.id))
    if existing:
        if existing.value == value:
            db.delete(existing)
            db.commit()
            return {"id": 0, "value": 0, "user_id": current_user.id, "word_id": word.id}
        existing.value = value
    else:
        new_vote = Vote(word_id=word.id, user_id=current_user.id, value=value)
        db.add(new_vote)
    
    db.commit()
    return db.scalar(select(Vote).where(Vote.word_id == word.id, Vote.user_id == current_user.id))

@router.post("/words/{slug}/comments", response_model=CommentResponse, summary="Comentar")
def create_comment(
    slug: str,
    comment_in: CommentCreate,
    db: Session = Depends(get_db),
    current_user: UserAuthToken = Depends(ensure_db_user)
):
    word = db.scalar(select(Word).where(Word.slug == slug))
    if not word:
        raise HTTPException(status_code=404, detail="Palabra no encontrada")
    
    new_comment = Comment(
        content=comment_in.content,
        word_id=word.id,
        author_id=current_user.id,
        parent_id=comment_in.parent_id
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment

@router.get("/words/{slug}/comments", response_model=List[CommentResponse], summary="Ver Hilo de Comentarios")
def list_comments(slug: str, db: Session = Depends(get_db)):
    word = db.scalar(select(Word).where(Word.slug == slug))
    if not word:
        raise HTTPException(status_code=404, detail="Inexistente")
    
    comments = db.scalars(
        select(Comment)
        .where(Comment.word_id == word.id, Comment.parent_id == None)
        .order_by(Comment.created_at.desc())
    ).all()
    return comments

# --- 4. MULTIMEDIA ---

@router.post("/words/{slug}/audio", summary="Subir Pronunciacion a Cloudinary")
def upload_word_audio(
    slug: str, 
    audio: UploadFile = File(...), 
    db: Session = Depends(get_db),
    current_user: UserAuthToken = Depends(ensure_db_user)
):
    word = db.scalar(select(Word).where(Word.slug == slug))
    if not word:
        raise HTTPException(status_code=404, detail="Palabra inexistente")

    audio_url = CloudinaryService.upload_audio(audio.file)
    word.audio_url = audio_url
    db.commit()
    return {"status": "success", "audio_url": audio_url}

# --- 5. MODERACION (Admin) ---

@router.put("/words/{slug}/approve", summary="Aprobar Palabra (Admin)")
def approve_word(
    slug: str, 
    db: Session = Depends(get_db),
    current_user: UserAuthToken = Depends(require_admin)
):
    word = db.scalar(select(Word).where(Word.slug == slug))
    if not word:
        raise HTTPException(status_code=404, detail="Palabra no encontrada")
    
    word.is_active = True
    db.commit()
    return {"status": "success", "message": "Palabra aprobada veci"}

# --- 6. TRIVIA ---

@router.get("/quiz/questions", response_model=List[QuizQuestionResponse], summary="Obtener Trivia Quitena")
def get_quiz_questions(db: Session = Depends(get_db)):
    questions = db.scalars(select(QuizQuestion).where(QuizQuestion.is_active == True)).all()
    return questions

@router.post("/quiz/questions/{id}/check", summary="Validar Respuesta")
def check_quiz_answer(
    id: int,
    answer_id: int = Query(...),
    db: Session = Depends(get_db)
):
    question = db.get(QuizQuestion, id)
    if not question:
        raise HTTPException(status_code=404, detail="No existe esa pregunta")
    
    from app.models.lexicon import QuizAnswer
    correct_answer = db.scalar(
        select(QuizAnswer)
        .where(QuizAnswer.question_id == id, QuizAnswer.is_correct == True)
    )
    
    is_correct = (correct_answer.id == answer_id) if correct_answer else False
    
    return {
        "is_correct": is_correct,
        "correct_id": correct_answer.id if correct_answer else None,
        "mensaje": "¡Qué bacán veci!" if is_correct else "¡Andas más perdido que el Panecillo!"
    }
