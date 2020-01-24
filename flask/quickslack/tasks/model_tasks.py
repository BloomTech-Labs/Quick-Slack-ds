from quickslack.app import create_celery_app
from quickslack.utils.app_mention import send_pred

celery = create_celery_app()

@celery.task(name='model_tasks.send_pred_task')
def send_pred_task(input_text, channel):
    print('celery running')
    send_pred(input_text, channel)
    return print('Clerey Task Ran')