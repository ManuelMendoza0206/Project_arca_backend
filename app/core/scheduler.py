import redis
from apscheduler.schedulers.background import BackgroundScheduler
from app.core.config import settings
from app.core.scheduler_jobs import generar_tareas_diarias

SCHEDULER_LOCK_KEY = "scheduler:generar_tareas_diarias_lock"
LOCK_TIMEOUT_SECONDS = 60 * 10

scheduler = BackgroundScheduler(timezone=settings.TIMEZONE)

def job_wrapper_generar_tareas():
    redis_client = None
    lock = None
    
    try:
        #Conectar con redis
        redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True
        )        

        lock = redis_client.lock(SCHEDULER_LOCK_KEY, timeout=LOCK_TIMEOUT_SECONDS)
        
        have_lock = lock.acquire(blocking=False)
        
        if have_lock:
            print("[Scheduler] Ejecutando generacion de tareas...")
            try:
                generar_tareas_diarias()
            finally:
                try:
                    lock.release()
                    print("Bloqueo liberado")
                except redis.exceptions.LockError:
                    print("No se pudo liberar el bloqueo")
        else:
            print("Bloqueo ocupado. Otro worker esta trabajando sin descanso")
            
    except redis.ConnectionError:
        print("[Scheduler] Error: No se pudo conectar a Redis")
    except Exception as e:
        print(f"Scheduler] Error inesperado en wrapper: {e}")
    finally:
        if redis_client:
            redis_client.close()

def setup_scheduler():
    print("Configurando APScheduler...")

    scheduler.add_job(
        job_wrapper_generar_tareas,
        trigger="cron",
        hour=15,
        minute=25,
        id="job_generar_tareas_diarias",
        name="Generar Tareas Recurrentes Diarias",
        replace_existing=True
    )

    if not scheduler.running:
        scheduler.start()
        print("APScheduler iniciado en segundo plano")