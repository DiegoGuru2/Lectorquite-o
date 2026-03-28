from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models.lexicon import Word, Category, Example, QuizQuestion, QuizAnswer, User, Comment, Vote
from datetime import datetime
import hashlib

def hash_pass(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def seed():
    db = SessionLocal()
    try:
        print("Sembrando léxico Quiteño Maestro (v3.0): 20 Palabras + 20 Preguntas...")

        # --- Usuarios ---
        u1 = User(id="dgurumendi-uid", email="dgurumendi@lectorquiteno.ec", full_name="Diego Gurumendi", hashed_password=hash_pass("12345678"), is_admin=True)
        u2 = User(id="veci-uid", email="veci@tienda.com", full_name="El Veci de la Tienda")
        db.add_all([u1, u2])
        db.flush()

        # --- Categorías ---
        cat_exp = Category(name="Expresion", description="Frases tipicas de la ciudad.")
        cat_sust = Category(name="Sustantivo", description="Nombres de cosas o personas.")
        cat_adj = Category(name="Adjetivo", description="Descriptivos.")
        db.add_all([cat_exp, cat_sust, cat_adj])
        db.flush()

        # --- 20 PALABRAS ---
        palabras_data = [
            ("Achachay", "achachay", "Expresión para indicar que hace mucho frío.", "Quichua", cat_exp),
            ("Arrarray", "arrarray", "Expresión para indicar que algo está muy caliente.", "Quichua", cat_exp),
            ("Aquisito nomás", "aquisito-nomas", "Indica que un lugar está muy cerca (aunque a veces no sea así).", "Coloquial", cat_exp),
            ("Guambra", "guambra", "Niño, joven o adolescente.", "Quichua", cat_sust),
            ("Ñaño", "nano", "Hermano o amigo muy cercano.", "Quichua", cat_sust),
            ("Mande", "mande", "Palabra de respeto para responder a un llamado o pedir repetición.", "Tradicional", cat_exp),
            ("No sea malito", "no-sea-malito", "Frase cortés para suavizar una petición o pedir un favor.", "Quiteñismo", cat_exp),
            ("Hacer la foca", "hacer-la-foca", "Pasar vergüenza o hacer quedar mal a alguien.", "Coloquial", cat_exp),
            ("Alhaja", "alhaja", "Algo bonito, bueno o de gran calidad.", "Español antiguo", cat_adj),
            ("Chulla vida", "chulla-vida", "Expresión para justificar disfrutar el momento, pues solo hay una vida.", "Tradicional", cat_sust),
            ("Asomarse", "asomarse", "Aparecer o visitar a alguien informalmente.", "Coloquial", cat_exp),
            ("Focazo", "focazo", "Algo impresionante o asombroso (positivo o negativo).", "Modismo", cat_adj),
            ("Langarote", "langarote", "Persona de gran estatura o muy alta.", "Coloquial", cat_adj),
            ("Tillos", "tillos", "Cuando algo es extremadamente fácil de realizar.", "Coloquial", cat_adj),
            ("Dios le pague", "dios-le-pague", "Forma tradicional y muy educada de dar las gracias.", "Religioso/Tradicional", cat_exp),
            ("Chance", "chance", "Dar una oportunidad o pedir un momento de espera.", "Anglicismo adaptado", cat_sust),
            ("Pana", "pana", "Amigo, compañero o camarada.", "Generalizado", cat_sust),
            ("Cachar", "cachar", "Entender o comprender plenamente un asunto.", "Coloquial", cat_exp),
            ("Quitof", "quitof", "Modismo juvenil de añadir una 'f' al final de las palabras.", "Juvenil", cat_exp),
            ("Simon", "simon", "Forma coloquial de decir Sí.", "Coloquial", cat_exp),
        ]

        for term, slug, meaning, origin, cat in palabras_data:
            w = Word(term=term, slug=slug, meaning=meaning, origin=origin, is_active=True)
            w.categories.append(cat)
            db.add(w)
        db.flush()

        # --- 20 PREGUNTAS DE TRIVIA ---
        trivias = [
            ("¿Con qué nombre es conocida popularmente la ciudad de Quito?", ["La Carita de Dios", "La Perla del Pacifico", "La Atenas de Ecuador"]),
            ("Si un quiteño te dice que algo está 'aquisito nomás', ¿qué significa?", ["Que está muy cerca", "Que está a 10 km", "Que no va a ir"]),
            ("¿Qué expresión usa un quiteño cuando tiene frío?", ["Achachay", "Arrarray", "Atatay"]),
            ("¿Qué significa la palabra 'guambra'?", ["Niño o joven", "Anciano", "Amigo"]),
            ("¿Qué palabra usa un quiteño para referirse a un amigo cercano?", ["Pana", "Veci", "Socio"]),
            ("¿Cómo se llama la figura que corona el cerro del Panecillo?", ["Virgen de Quito", "Cristo del Consuelo", "Ángel de la Guarda"]),
            ("¿Qué significa la frase 'no sea malito'?", ["Pedido de favor cortés", "Estar enojado", "Ser una mala persona"]),
            ("¿Qué es un 'llapingacho'?", ["Tortillas de papa con huevo", "Un tipo de pan", "Una bebida"]),
            ("Si alguien pide que le des 'haciendo una cosa', ¿qué pide?", ["Que la hagas por él", "Que no la hagas", "Que le enseñes"]),
            ("¿Qué significa que algo está 'alhaja'?", ["Que es bonito", "Que es feo", "Que es caro"]),
            ("¿Qué es el 'canelazo'?", ["Bebida caliente de canela", "Un postre", "Un tipo de baile"]),
            ("¿Cómo se llama el juego de cartas tradicional de Quito?", ["El 40", "El 15", "Poker"]),
            ("¿Qué significa 'hacer la foca'?", ["Quedar en vergüenza", "Bailar muy bien", "Ir al zoológico"]),
            ("¿Qué es un 'chulla' quiteño?", ["Alguien típico y único", "Un tipo de zapato", "Un traje formal"]),
            ("¿Qué significa 'cachar' en el habla coloquial?", ["Entender", "Comprar", "Correr"]),
            ("¿Qué expresión utiliza un quiteño para agradecer?", ["Dios le pague", "Chao", "De nada"]),
            ("Si alguien dice 'dame un chance', ¿qué pide?", ["Una oportunidad", "Dinero", "Un cigarrillo"]),
            ("¿Qué palabra indica que algo quema o hace mucho calor?", ["Arrarray", "Achachay", "Atatay"]),
            ("¿Es común usar artículos (El/La) antes de nombres propios en Quito?", ["Sí, es muy común", "No, nunca", "Solo en documentos"]),
            ("¿Qué significa que algo esté 'tillos'?", ["Que es fácil", "Que está sucio", "Que es difícil"])
        ]

        for question_text, answers in trivias:
            q = QuizQuestion(question=question_text, is_active=True)
            db.add(q)
            db.flush()
            # La primera respuesta de la lista es la CORRECTA siempre en esta lógica
            for i, ans_text in enumerate(answers):
                db.add(QuizAnswer(answer_text=ans_text, is_correct=(i == 0), question_id=q.id))

        db.commit()
        print("Éxito Maestro: 22 Palabras y 21 Preguntas listas en la base de datos.")

    except Exception as e:
        print(f"Error durante la siembra v3.0: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed()
