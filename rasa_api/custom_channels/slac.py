from rasa.core.channels.slack import InputChannel

class SlackBotV2(InputChannel):
    @classmethod
    def name(cls):
        return "slacks"
