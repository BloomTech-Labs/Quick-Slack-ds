from ..extensions import db


class Message(db.Model):
    db_id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.String(36), nullable=True)
    user_id = db.Column(db.String(20), nullable=True)
    ts = db.Column(db.Float(), nullable=False)
    reply_count = db.Column(db.Integer, default=0)
    text = db.Column(db.Text, nullable=True)
    channel_id = db.Column(db.ForeignKey('channel.channel_id'), nullable=False)
    channel = db.relationship(
        'Channel', backref=db.backref('messages', lazy='dynamic'))

    def __repr__(self):
        return f'<Message {self.message_id}>'


class Reply(db.Model):
    db_id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.String(36), nullable=True)
    user_id = db.Column(db.String(20), nullable=True)
    ts = db.Column(db.Float(), nullable=True)
    text = db.Column(db.Text, nullable=True)
    thread_ts = db.Column(db.Float())
    channel_id =db.Column(db.ForeignKey('channel.channel_id'), nullable=False)

    def __repr__(self):
        return f'<Message {self.message_id}>'


class Channel(db.Model):
    db_id = db.Column(db.Integer, primary_key=True)
    channel_id = db.Column(db.String(10), unique=True)
    channel_name = db.Column(db.String(100))
    def __repr__(self):
        return f'<Message {self.channel_id}>'
