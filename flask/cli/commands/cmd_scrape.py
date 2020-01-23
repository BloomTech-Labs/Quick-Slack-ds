import click

from quickslack.app import create_app
from quickslack.extensions import db
from slack_user_client import SlackClient
from decouple import config
from quickslack.schemas import Reply, Message, Channel
from tqdm import tqdm
import json
from json.decoder import JSONDecodeError
app = create_app()
db.app = app


@click.group()
def cli():
    """ Slack Scraper """
    pass


@click.command()
def all_messages():
    slack = SlackClient(
        config('SLACK_EMAIL'), config('SLACK_PASSWORD'),
        config('SLACK_WORKSPACE_URL'))
    slack.login()
    channels = slack.get_boot_data()['channels']
    all_channels = slack.get_all_channels()
    private_ids = [c['id'] for c in channels if c['is_private']]
    public_channels = [c for c in all_channels if c['id'] not in private_ids]
    channels_to_add = []
    # Add joined public channel.
    # For some reasons these don't show up on searches with the
    # query: ''
    public_channels = public_channels + \
                      [c for c in channels if not c['is_private']]
    public_channels = {p['id']: p for p in public_channels}.values()
    for channel in public_channels:
        channels_to_add.append(Channel(
            channel_id=channel['id'], channel_name=channel['name']))
    db.session.add_all(channels_to_add)
    db.session.commit()
    for channel in tqdm(public_channels):
        messages = slack.get_all_messages_from_channel(channel['id'])
        messages = [m for m in messages if m.get('client_msg_id')]
        messages = {m['client_msg_id']: m for m in messages}.values()
        db.session.add_all(
            [
                Message(
                    message_id=m['client_msg_id'], user_id=m['user'],
                    text=m['text'], ts=float(m['ts']),
                    reply_count=int(m.get('reply_count') or 0),
                    channel_id=channel['id']
                )
                for m in messages
            ]
        )
        db.session.commit()
        thread_ts = [m['ts'] for m in messages if m.get('reply_count')]
        for tts in thread_ts:
            try:
                replies = slack.get_all_replies(channel['id'], tts)
            except JSONDecodeError:
                app.logger.info("No reply")
                continue
            replies = [r for r in replies if r.get('client_msg_id')]
            replies = {r['client_msg_id']: r for r in replies}.values()
            db.session.add_all(
                [Reply(
                    thread_ts=tts, ts=r['ts'],
                    message_id=r['client_msg_id'],
                    user_id=r['user'],
                    text=r['text'],
                    channel_id=channel['id']
                )
                    for r in replies]
            )
            db.session.commit()


cli.add_command(all_messages)
