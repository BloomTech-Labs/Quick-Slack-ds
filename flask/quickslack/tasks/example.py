from quickslack.app import create_celery_app

celery = create_celery_app()

@celery.task()
def first_task():
    print('Wheres Waldo?')

    print('gotcha bitch (in dave chapelles voice)')

    return None