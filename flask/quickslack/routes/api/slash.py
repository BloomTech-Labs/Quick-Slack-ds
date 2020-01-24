from flask import Blueprint, jsonify, request, render_template, flash, escape
from flask import current_app as app

slash = Blueprint('slash', __name__)


@slash.route('/slash', methods=['GET', 'POST'])
def recieve():
    print('slash command incoming')
    try:
        channel = escape(request.form['channel_id'])
        input_text = escape(request.form['text'])
    except Exception as e:
        return jsonify('Im broken, blame it on richard')

    if not input_text:
        return jsonify("Stop tryina break things Richard!")

    print('starting celery')
    from quickslack.tasks.model_tasks import send_pred_task
    send_pred_task.delay(input_text, channel)

    return jsonify({"success": True})
