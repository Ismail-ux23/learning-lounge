from celery import Celery
from app import create_app
app=create_app()
celery=Celery('learning_lounge',broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(beat_schedule={'deadlines-every-15-seconds':{'task':'lounge.sweep','schedule':15.0}},task_acks_late=True,worker_prefetch_multiplier=1,timezone='UTC')
@celery.task(name='lounge.sweep')
def sweep():
    with app.app_context():
        from app.services.assessment import sweep_expired
        sweep_expired()
