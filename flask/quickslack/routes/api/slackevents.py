from flask import Blueprint, jsonify, request, render_template, flash
from flask import current_app as app

slackevents = Blueprint('slackevents', __name__)


@slackevents.route('/slackevents', methods=['GET', 'POST'])
def recieve():
    print('incoming event')
    content = request.get_json(silent=True)
    payload={}
    print(content)

    try:
        print('get event data')
        event_type = content['event']['type']
        print(event_type)

        if event_type == 'app_mention':
            print('Its an app mention')

            payload['thread_ts'] = content['event']['thread_ts']
            payload['event_ts'] = content['event']['event_ts']

            payload['input_text'] = content['event']['text'].replace("<@UT1EE1GQM> ", "")
            payload['channel'] = content['event']['channel']

            print('Starting celery')
            from quickslack.tasks.model_tasks import send_pred_task
            send_pred_task.delay(payload)
    except: print('ERROR')

    return jsonify(content)
