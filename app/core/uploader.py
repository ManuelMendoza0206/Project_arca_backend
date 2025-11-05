import cloudinary
import cloudinary.uploader
from fastapi import UploadFile, HTTPException, status
from typing import Dict

from app.core.config import settings

def configure_cloudinary():
    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
        secure=True
    )
configure_cloudinary()

def upload_to_cloudinary(file: UploadFile, folder: str) -> Dict:
    try:
        upload_result = cloudinary.uploader.upload(
            file.file,
            folder=f"zooconnect/{folder}",
            resource_type="auto"
        )
        return upload_result
    except Exception as e:
        print(f"Error al subir a Cloudinary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocurrio un error al subir el archivo"
        )

def delete_from_cloudinary(public_id: str):
    try:
        cloudinary.uploader.destroy(public_id)
    except Exception as e:
        print(f"Error al eliminar de Cloudinary (public_id: {public_id}): {e}")