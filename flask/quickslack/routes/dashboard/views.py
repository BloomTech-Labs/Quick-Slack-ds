import json, requests

from flask import Blueprint, jsonify, request, render_template, flash
from flask import current_app as app
from .forms import Channel, Text

dashboard = Blueprint('dashboard', __name__)

url = 'http://model:8080/predict'
input_text = 'My favorite flavor of ice cream is'


@dashboard.route('/dashboard', methods=['GET', 'POST'])
def dashboard_display():
    channel_form = Channel()
    text_form = Text()

    render_args=['dashboard/pages/payload.html']
    render_kwargs = {
        'channel_form': channel_form,
        'text_form': text_form,
        'payload': [],
        'include_logs': False

    }

    if channel_form.submit.data and channel_form.validate_on_submit():

        channel_id = request.form.get('channel_id')

        render_kwargs['payload'] = app.config['slack'].get_all_messages_from_channel(channel_id)

        flash(f'{channel_id} has been scrapped', 'success')
        return render_template(*render_args, **render_kwargs)

    if text_form.submit.data and text_form.validate_on_submit():

        input_text = request.form.get('input_text')

        val = {'input_text': input_text}
        render_kwargs['payload'] = [requests.post(url, data=json.dumps(val)).json()]

        flash(f'{input_text}', 'success')
        return render_template(*render_args, **render_kwargs)

    return render_template(*render_args, **render_kwargs)