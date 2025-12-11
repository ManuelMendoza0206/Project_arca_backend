from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.session import SessionLocal
from app.models.tarea import TipoTarea
from app.models.inventario import TipoSalida

def init_db():
    db = SessionLocal()
    try:
        print("--- Iniciando Semillas (Seeds) ---")

        # 1. ROLES
        print("1. Verificando Roles...")
        roles_sql = """
        INSERT INTO roles (id, name) VALUES 
        (1, 'administrador'),
        (2, 'visitante'),
        (3, 'cuidador'),
        (4, 'veterinario')
        ON CONFLICT (id) DO NOTHING;
        """
        db.execute(text(roles_sql))
        
        print("2. Verificando Tipos de Tarea...")
        
        if not db.query(TipoTarea).filter_by(id_tipo_tarea=1).first():
            db.add(TipoTarea(
                id_tipo_tarea=1, 
                nombre_tipo_tarea="Alimentacion",
                descripcion_tipo_tarea="Tareas relacionadas con dar de comer a los animales",
                is_active=True
            ))

        if not db.query(TipoTarea).filter_by(id_tipo_tarea=2).first():
            print("   + Creando Tipo Tarea: Tratamiento Médico")
            db.add(TipoTarea(
                id_tipo_tarea=2, 
                nombre_tipo_tarea="Tratamiento Médico",
                descripcion_tipo_tarea="Administración de medicamentos y curaciones",
                is_active=True
            ))
        
        print("3. Verificando Tipos de Salida...")

        if not db.query(TipoSalida).filter_by(id_tipo_salida=1).first():
            db.add(TipoSalida(
                id_tipo_salida=1,
                nombre_tipo_salida="Consumo Alimentación",
                descripcion_tipo_salida="Salida automática generada por tareas de alimentación",
                is_active=True
            ))

        if not db.query(TipoSalida).filter_by(id_tipo_salida=2).first():
            print("   + Creando Tipo Salida: Consumo Tratamiento")
            db.add(TipoSalida(
                id_tipo_salida=2,
                nombre_tipo_salida="Consumo Tratamiento",
                descripcion_tipo_salida="Salida automática por aplicación de medicamentos",
                is_active=True
            ))

        db.commit()
        print("--- Datos cargados exitosamente (10/10) ---")

    except Exception as e:
        print(f"!!! Error cargando datos iniciales: {e}")
        db.rollback()
    finally:
        db.close()