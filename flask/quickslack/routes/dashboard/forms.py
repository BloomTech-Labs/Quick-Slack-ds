from flask_wtf import FlaskForm
from wtforms_components import StringField
from wtforms import SubmitField
from wtforms.validators import DataRequired, Length

class Channel(FlaskForm):
    channel_id = StringField(
        'Channel ID',
        validators=[DataRequired(), Length(min=2, max=20)]
    )
    submit = SubmitField('Start Test')

class Text(FlaskForm):
    input_text = StringField(
        'Input Text',
        validators=[DataRequired(), Length(min=2, max=50)]
    )
    submit = SubmitField('Start Test')