from decouple import config
from datetime import timedelta
from celery.schedules import crontab

# if config('FLASK_ENV') == 'development':
#     DEBUG = True
# else:
#     DEBUG = False

DEBUG = False

SECRET_KEY = config('SECRET_KEY')
# SERVER_NAME = '127.0.0.1:8000'

CELERY_BROKER_URL = 'redis://:devpassword@redis:6379/0'
CELERY_RESULT_BACKEND = 'redis://:devpassword@redis:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_REDIS_MAX_CONNECTIONS = 5
CELERYBEAT_SCHEDULE = {
    'task_name': {
        'task': 'quickslack.tasks.example.first_task',
        'schedule': 30.0
    },
}

DB_NAME = config('DB_NAME')
DB_USER = config('DB_USER')
DB_PASS = config('DB_PASS')
DB_SERVICE = config('DB_SERVICE')
DB_PORT = config('DB_PORT')
SQLALCHEMY_DATABASE_URI = 'postgresql://{0}:{1}@{2}:{3}/{4}'.format(
    DB_USER, DB_PASS, DB_SERVICE, DB_PORT, DB_NAME
)
SQLALCHEMY_TRACK_MODIFICATIONS = False