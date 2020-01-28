from rasa.core.channels.slack import SlackBot, SlackInput
from sanic import Blueprint, response
from typing import Text, Optional, List, Dict, Any, Callable, Awaitable
import logging
import json
from sanic.request import Request
from rasa.core.channels.channel import UserMessage, OutputChannel

logger = logging.getLogger(__name__)


class SlackBot(SlackInput):
    @classmethod
    def name(cls):
        return "slackv2"

    def get_metadata(self, request: Request) -> Optional[Dict[Text, Any]]:
        logger.warning("Get Metadata - ")
        metadata = super().get_metadata(request) or {}
        if request.json:
            data = request.json
            logger.info(data)
            thread_ts = data['event'].get('thread_ts')
            metadata.update({'thread_ts': thread_ts, 'x': 1})
            logger.info(metadata)
            repr(metadata)
            return metadata
        return metadata
