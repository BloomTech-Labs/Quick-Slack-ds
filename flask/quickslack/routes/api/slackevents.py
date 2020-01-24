from flask import Blueprint, jsonify, request, render_template, flash
from flask import current_app as app

slackevents = Blueprint('slackevents', __name__)


@slackevents.route('/slackevents', methods=['GET', 'POST'])
def recieve():
    print('event incoming')
    try:
        content = request.get_json(silent=True)
        print(content)
    except Exception as e:
        return jsonify(e)

    input_text = content['event']['text'].replace("<@UT1EE1GQM> ", "")
    channel = content['event']['channel']

    print(input_text, channel)

    print('starting celery')
    from quickslack.tasks.model_tasks import send_pred_task
    send_pred_task.delay(input_text, channel)

    return jsonify({"success": True})
