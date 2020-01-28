from rasa.core.channels.slack import  SlackBot, SlackInput
from sanic import Blueprint, response
from typing import Text, Optional, List, Dict, Any, Callable, Awaitable
import logging
import json
from sanic.request import Request
from rasa.core.channels.channel import UserMessage, OutputChannel

logger = logging.getLogger(__name__)

class SlackOutput(SlackBot):
    async def send_text_message(
            self, recipient_id: Text, text: Text, **kwargs: Any
    ) -> None:
        recipient = self.slack_channel or recipient_id
        for message_part in text.split("\n\n"):
            super().api_call(
                "chat.postMessage",
                channel=recipient,
                as_user=True,
                text=message_part,
                type="mrkdwn",
            )


class SlackBotV1(SlackInput):
    def __init__(self):
        return 1/0
    @classmethod
    def name(cls):
        return "slackv2"

    def get_metadata(self, request: Request) -> Optional[Dict[Text, Any]]:
        assert(1/0)
        logger.warning("Get Metadata")
        if request.json:
            data = request.json
            thread_ts = data['message'].get('thread_ts')
            return {'thread_ts': thread_ts, 'x': 1}
        return {"Metadata": 12}
