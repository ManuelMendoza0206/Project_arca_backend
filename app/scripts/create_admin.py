import logging
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.user import User
from app.models.role import Role
from app.core.security import get_password_hash
from app.core.enums import UserRole
from app.crud.user import get_user_by_email

logger = logging.getLogger(__name__)

DEFAULT_ADMIN_EMAIL = "admin@zconnect.com"
DEFAULT_ADMIN_PASSWORD = "admin123"

def create_default_admin():
    db: Session = SessionLocal()
    try:
        admin_role_name = UserRole.ADMINISTRADOR.value
        db_admin_role = db.query(Role).filter(Role.name == admin_role_name).first()

        if not db_admin_role:
            logger.info(f"El rol '{admin_role_name}' no existe. vamos a crearlo")
            db_admin_role = Role(name=admin_role_name) 
            db.add(db_admin_role)
            db.commit()
            db.refresh(db_admin_role)
            logger.info("Rol 'ADMINISTRADOR' creado exitosamente")

        existing_admin = get_user_by_email(db, email=DEFAULT_ADMIN_EMAIL)

        if existing_admin:
            logger.info(f"El usuario administrador ({DEFAULT_ADMIN_EMAIL}) ya existe")
            return

        logger.info(f"Creando usuario administrador por defecto: {DEFAULT_ADMIN_EMAIL}")
        hashed_password = get_password_hash(DEFAULT_ADMIN_PASSWORD)

        admin_user = User(
            email=DEFAULT_ADMIN_EMAIL,
            username="admin",
            hashed_password=hashed_password,
            is_active=True,
            role_id=db_admin_role.id 
        )

        db.add(admin_user)
        db.commit()
        logger.info(f"Usuario administrador ({DEFAULT_ADMIN_EMAIL}) creado exitosamente")

    except Exception as e:
        logger.error(f"Error al crear el usuario administrador por defecto: {e}", exc_info=True)
        db.rollback()
    finally:
        db.close()