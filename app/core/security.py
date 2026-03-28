import os
import requests
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database import get_db
from app.models.lexicon import User

# --- SEGURIDAD AVANZADA (TIER 1) ---
security = HTTPBearer()

class UserAuthToken(BaseModel):
    id: str # Supabase UID
    email: str
    is_admin: bool = False

def get_current_user(token: HTTPAuthorizationCredentials = Depends(security)) -> UserAuthToken:
    """
    Decodifica y valida el token JWT de Supabase Auth.
    Soporta validacion simetrica (HS256) y asimetrica (RS256/ES256) via JWKS.
    """
    try:
        # 1. Obtencion de cabecera no verificada para saber el algoritmo
        unverified_header = jwt.get_unverified_header(token.credentials)
        alg = unverified_header.get("alg")

        # 2. Decodificacion Segun Algoritmo (Estandar Arrechoteca)
        if alg == "HS256":
            # Validacion simetrica usando el JWT Secret del dashboard de Supabase
            payload = jwt.decode(
                token.credentials, 
                settings.SUPABASE_JWT_SECRET, 
                algorithms=["HS256"],
                audience="authenticated"
            )
        else:
            # Validacion asimetrica (Premium) obteniendo claves publicas de Supabase
            jwks_url = f"{settings.supabase_url.rstrip('/')}/auth/v1/.well-known/jwks.json"
            jwks = requests.get(jwks_url).json()
            payload = jwt.decode(
                token.credentials,
                jwks,
                algorithms=[alg],
                audience="authenticated"
            )
        
        user_id = payload.get("sub")
        email = payload.get("email")
        user_metadata = payload.get("user_metadata", {})
        is_admin = user_metadata.get("is_admin", False)

        if not user_id or not email:
            raise HTTPException(status_code=401, detail="Token de Supabase incompleto")
            
        return UserAuthToken(id=user_id, email=email, is_admin=is_admin)

    except JWTError as e:
        print(f"JWT Verification Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Error al validar el acceso con Supabase (Token invalido o expirado)"
        )
    except Exception as e:
        print(f"Unexpected Auth Error: {str(e)}")
        raise HTTPException(status_code=401, detail="Falla en verificacion de identidad")

def ensure_db_user(
    current_user: UserAuthToken = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> UserAuthToken:
    """
    Asegura que el usuario autenticado exista en la base de datos local.
    Sincronizacion automatica para integridad de comentarios y votos.
    """
    user = db.get(User, current_user.id)
    if not user:
        user = User(
            id=current_user.id,
            email=current_user.email,
            full_name=current_user.email.split("@")[0],
            is_admin=current_user.is_admin
        )
        db.add(user)
        db.commit()
    return current_user

def require_admin(current_user: UserAuthToken = Depends(ensure_db_user)) -> UserAuthToken:
    """
    Proteccion para rutas de moderacion y administracion avanzada.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado: Se requiere perfil de administrador"
        )
    return current_user
