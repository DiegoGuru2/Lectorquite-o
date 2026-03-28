import cloudinary
import cloudinary.uploader
from app.core.config import settings
from typing import Optional

# --- CONFIGURACION ---
# Esto lee directamente de tu .env
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True
)

class CloudinaryService:
    @staticmethod
    def upload_image(file_obj, folder: str = "lexico_quiteno/images") -> str:
        """
        Sube la imagen de la 'Palabra del dia' a la nube.
        Devuelve la URL publica (HTTPS).
        """
        response = cloudinary.uploader.upload(file_obj, folder=folder)
        return response.get("secure_url")

    @staticmethod
    def upload_audio(file_obj, folder: str = "lexico_quiteno/pronunciacion") -> str:
        """
        Sube el audio del dialecto quiteno para multimedia.
        Usa resource_type='video' (Cloudinary usa este para audio tambien).
        """
        response = cloudinary.uploader.upload(
            file_obj, 
            folder=folder, 
            resource_type="video" # Especifico para audios
        )
        return response.get("secure_url")

    @staticmethod
    def delete_asset(public_id: str):
        """
        Elimina el recurso en caso de rechazo de moderacion.
        """
        cloudinary.uploader.destroy(public_id)
