from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.endpoints import lexicon

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Motor de léxico y trivia interactiva del dialecto de Quito (Basado en Clean Architecture).",
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# --- 1. CONFIGURACION DE CORS (Dinamico) ---
# En produccion esto vendria de settings.BACKEND_CORS_ORIGINS en el .env
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8000",
    "http://localhost:5173", # Vite (Frontend)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 2. RUTAS ---
app.include_router(
    lexicon.router, 
    prefix=f"{settings.API_V1_STR}/lexicon", 
    tags=["Léxico Quiteño 🏁"]
)

@app.get("/", tags=["Estado"])
def read_root():
    return {
        "mensaje": "¡Qué cosita veci! El backend del Lector Quiteño está activof.", 
        "estado": "Online",
        "docs": "/docs"
    }
