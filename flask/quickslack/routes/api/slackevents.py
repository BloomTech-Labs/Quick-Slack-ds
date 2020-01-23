from flask import Blueprint, jsonify, request, render_template, flash
from flask import current_app as app

slackevents = Blueprint('slackevents', __name__)


@slackevents.route('/slackevents', methods=['GET', 'POST'])
def recieve():

    try:
        content = request.get_json(silent=True)
        print(content)
    except Exception as e:
        return jsonify(e)
    
    return None
