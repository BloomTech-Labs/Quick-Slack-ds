from .modelapi import get_pred

import slack, requests
from decouple import config

client = slack.WebClient(config('SLACK_TOKEN'))

def send_pred(input_text, channel):

    pred = get_pred(input_text)

    response = client.chat_postMessage(
        channel=channel,
        text=pred['output_text']
    )
    assert response["ok"]