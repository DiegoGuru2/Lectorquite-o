from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import List, Optional
from datetime import datetime

# --- Paginacion ---
class PagedResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List

# --- Usuarios ---
class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str # Supabase UID es texto
    email: str
    full_name: Optional[str] = None
    is_admin: bool

# --- Comentarios ---
class CommentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    content: str
    created_at: datetime
    author_id: str
    word_id: int
    parent_id: Optional[int] = None
    replies: List["CommentResponse"] = []

class CommentCreate(BaseModel):
    content: str
    # word_id: int # El slug suele ser el identificador en la URL
    parent_id: Optional[int] = None

# --- Votos ---
class VoteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    value: int
    user_id: str
    word_id: int

# --- Trivia ---
class QuizAnswerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    answer_text: str
    is_correct: Optional[bool] = None

class QuizQuestionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    question: str
    answers: List[QuizAnswerResponse]

# --- Lexico (Palabras) ---
class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    description: Optional[str] = None

class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None

class ExampleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    sentence: str
    translation: Optional[str] = None

class WordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    term: str
    slug: str
    meaning: str
    origin: Optional[str] = None
    audio_url: Optional[str] = None
    image_url: Optional[str] = None
    is_active: bool
    is_featured: bool
    created_at: datetime
    categories: List[CategoryResponse]
    examples: List[ExampleResponse]
    vote_count: Optional[int] = 0
    comment_count: Optional[int] = 0

class WordCreate(BaseModel):
    term: str
    slug: str
    meaning: str
    origin: Optional[str] = None
    category_ids: Optional[List[int]] = None

class WordUpdate(BaseModel):
    term: Optional[str] = None
    meaning: Optional[str] = None
    origin: Optional[str] = None
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None
    category_ids: Optional[List[int]] = None

class WordPaged(PagedResponse):
    items: List[WordResponse]
