from pathlib import Path
from app.core.config import settings

def ensure_upload_dirs_exist():
    base_path = Path(settings.MEDIA_DIR)
    subdirs = ["animals", "habitats", "users"]
    base_path.mkdir(parents=True, exist_ok=True)
    for sub in subdirs:
        (base_path / sub).mkdir(parents=True, exist_ok=True)
    print(f"Directorios de media asegurados en: {base_path.resolve()}")
