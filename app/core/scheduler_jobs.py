from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta
from croniter import croniter
from app.db.session import SessionLocal
from app.models.tarea import TareaRecurrente, Tarea

def generar_tareas_diarias():

    db: Session = SessionLocal()
    print(f"[{datetime.now()}] Iniciando job: 'generar_tareas_diarias'...")

    try:
        today = date.today()
        
        #obtener plantillas activas
        plantillas = db.query(TareaRecurrente).filter(
            TareaRecurrente.is_active == True
        ).all()

        tareas_creadas_count = 0
        errores_count = 0

        for plantilla in plantillas:
            try:
                midnight_today = datetime(today.year, today.month, today.day, 0, 0)
                base_time = midnight_today - timedelta(seconds=1) 
                
                cron = croniter(plantilla.frecuencia_cron, base_time)
                next_run = cron.get_next(datetime)

                if next_run.date() != today:
                    continue

                tarea_existente = db.query(Tarea).filter(
                    Tarea.tarea_recurrente_id == plantilla.id_tarea_recurrente,
                    Tarea.fecha_programada == today
                ).first()

                if tarea_existente:
                    continue

                print(f" + Creando tarea automatica: '{plantilla.titulo_plantilla}'...")

                nueva_tarea = Tarea(
                    titulo=plantilla.titulo_plantilla,
                    descripcion_tarea=plantilla.descripcion_plantilla,
                    tipo_tarea_id=plantilla.tipo_tarea_id,
                    animal_id=plantilla.animal_id,
                    habitat_id=plantilla.habitat_id,
                    tarea_recurrente_id=plantilla.id_tarea_recurrente,
                    fecha_programada=today,
                    usuario_asignado_id=plantilla.usuario_asignado_id, 
                    
                    is_completed=False
                )

                db.add(nueva_tarea)
                db.commit() 
                tareas_creadas_count += 1

            except Exception as e_inner:
                db.rollback()
                errores_count += 1
                print(f"Error procesando plantilla ID {plantilla.id_tarea_recurrente}: {e_inner}")
                continue

        print(f"Job completado. Creadas: {tareas_creadas_count}. Errores: {errores_count}")

    except Exception as e:
        print(f" ERROR El job 'generar_tareas_diarias' fallo a nivel general: {e}")
    
    finally:
        db.close()