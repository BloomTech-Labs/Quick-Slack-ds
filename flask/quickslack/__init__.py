
from .app import create_app, create_celery_app

APP = create_app()
CELERY = create_celery_app()