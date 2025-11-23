from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.session import SessionLocal
from app.models.tarea import TipoTarea
from app.models.inventario import TipoSalida

def init_db():

    db = SessionLocal()
    try:

        print("Creacion de roles..")
        roles_sql = """
        INSERT INTO roles (id, name) VALUES 
        (1, 'administrador'),
        (4, 'veterinario'),
        (3, 'cuidador'),
        (2, 'visitante')
        ON CONFLICT (id) DO NOTHING;
        """
        db.execute(text(roles_sql))
        
        #TIPOTAREA
        tipo_tarea_alim = db.query(TipoTarea).filter(TipoTarea.id_tipo_tarea == 1).first()
        if not tipo_tarea_alim:
            print("Creando Tipo de Tarea 'Alimentación'.")
            t_tarea = TipoTarea(
                id_tipo_tarea=1, 
                nombre_tipo_tarea="Alimentacion",
                descripcion_tipo_tarea="Tareas relacionadas con dar de comer a los animales",
                is_active=True
            )
            db.add(t_tarea)
        
        #TIPOSALIDA
        tipo_salida_alim = db.query(TipoSalida).filter(TipoSalida.id_tipo_salida == 1).first()
        if not tipo_salida_alim:
            print("Creando Tipo de Salida")
            t_salida = TipoSalida(
                id_tipo_salida=1,
                nombre_tipo_salida="Consumo Alimentacion",
                descripcion_tipo_salida="Salida automática generada por tareas de alimentacion",
                is_active=True
            )
            db.add(t_salida)

        db.commit()
        print("Datos correctamente cargados10/10")

    except Exception as e:
        print(f"Error cargando datos iniciales: {e}")
        db.rollback()
    finally:
        db.close()