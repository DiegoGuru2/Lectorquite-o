from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Lector Quiteño Backend"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Base de Datos
    DATABASE_URL: str
    
    # Seguridad (Local)
    SECRET_KEY: str = "dev-secret-key-quito-123"
    
    # --- SUPABASE ---
    SUPABASE_URL: str = "https://example.supabase.co"
    SUPABASE_JWT_SECRET: str = "tu-secreto-jwt-aqui"
    
    # --- CLOUDINARY ---
    CLOUDINARY_CLOUD_NAME: Optional[str] = "tu-cloud-name"
    CLOUDINARY_API_KEY: Optional[str] = "tu-api-key"
    CLOUDINARY_API_SECRET: Optional[str] = "tu-api-secret"

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="allow" # Permite otros campos sin fallar
    )

settings = Settings()
