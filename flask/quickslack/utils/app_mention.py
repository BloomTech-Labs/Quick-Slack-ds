from .modelapi import get_pred

import slack, requests
from decouple import config

client = slack.WebClient(config('SLACK_TOKEN'))

def send_pred(payload):

    pred = get_pred(payload['input_text'])

    if payload['thread_ts'] == payload['event_ts']:
        slack_kwargs = {
            'channel': payload['channel'],
            'text': pred['output_text']
        }
    else:
        slack_kwargs = {
            'token': config('USER_TOKEN'),
            'channel': payload['channel'],
            'thread_ts': payload['thread_ts'],
            'text': pred['output_text'],
            'as_user': True
        }

    response = client.chat_postMessage(**slack_kwargs)
    assert response["ok"]