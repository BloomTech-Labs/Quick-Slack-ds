from rasa.core.channels.slack import SlackBot, SlackInput
from sanic import Blueprint, response
from typing import Text, Optional, List, Dict, Any, Callable, Awaitable
import logging
import json
from sanic.request import Request
from rasa.core.channels.channel import UserMessage, OutputChannel
import aiojobs
logger = logging.getLogger(__name__)


class SlackBotOutput(SlackBot):
    @classmethod
    def name(cls):
        return "slackv2"

    def __init__(self, token: Text,
                 slack_channel: Optional[Text] = None,
                 thread_ts: Optional[Text] = None) -> None:
        logger.info("Output Initialized")
        self.thread_ts = thread_ts
        super().__init__(token, slack_channel)

    async def send_text_message(
            self, recipient_id: Text, text: Text, **kwargs: Any
    ) -> None:
        logger.info("send_text_message")
        logger.info(kwargs)
        # await super().send_text_message(recipient_id, text, **kwargs)
        recipient = self.slack_channel or recipient_id
        thread_ts = self.thread_ts
        logger.info(f"sending thread_ts {thread_ts}")
        for message_part in text.split("\n\n"):
            super().api_call(
                "chat.postMessage",
                channel=recipient,
                as_user=True,
                thread_ts=thread_ts,
                text=message_part,
                type="mrkdwn",
            )


class SlackBotInput(SlackInput):
    @classmethod
    def name(cls):
        return "slackv2"

    def __init__(self, *args, **kwargs):
        logger.info("Input Init")

        super().__init__(*args, **kwargs)

    def get_metadata(self, request: Request) -> Optional[Dict[Text, Any]]:
        metadata = super().get_metadata(request) or {}
        if request.json:
            data = request.json
            logger.info(data)
            thread_ts = data['event'].get('thread_ts')
            channel = data['event'].get('channel')
            ts = data['event'].get('ts')
            metadata.update(
                {'thread_ts': thread_ts, 'ts': ts, 'channel': channel})
            logger.info(metadata)
            repr(metadata)
            return metadata
        return metadata

    async def process_message(
            self,
            request: Request,
            on_new_message: Callable[[UserMessage], Awaitable[Any]],
            text,
            sender_id: Optional[Text],
            metadata: Optional[Dict],
    ) -> Any:
        """Slack retries to post messages up to 3 times based on
        failure conditions defined here:
        https://api.slack.com/events-api#failure_conditions
        """
        retry_reason = request.headers.get(self.retry_reason_header)
        retry_count = request.headers.get(self.retry_num_header)
        thread_ts = metadata.get('thread_ts') or metadata.get('ts')
        channel = metadata.get('channel')
        logger.info(f"METADATA: {metadata}")
        if retry_count and retry_reason in self.errors_ignore_retry:
            logger.warning(
                f"Received retry #{retry_count} request from slack"
                f" due to {retry_reason}."
            )

            return response.text(None, status=201,
                                 headers={"X-Slack-No-Retry": 1})

        try:
            out_channel = self.get_output_channel(
                channel=channel, thread_ts=thread_ts)
            user_msg = UserMessage(
                text,
                out_channel,
                sender_id,
                input_channel=self.name(),
                metadata=metadata,
            )

            scheduler = await aiojobs.create_scheduler()
            await scheduler.spawn(on_new_message(user_msg))
        except Exception as e:
            logger.error(f"Exception when trying to handle message.{e}")
            logger.error(str(e), exc_info=True)

        return response.text("")

    def get_output_channel(self, channel=None, thread_ts=None) -> OutputChannel:
        channel = channel or self.slack_channel
        return SlackBotOutput(self.slack_token, channel, thread_ts)
