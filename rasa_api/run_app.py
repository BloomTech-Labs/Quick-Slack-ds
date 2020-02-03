# from rasa.core.channels import HttpInputChannel
from rasa.core.agent import Agent
# from rasa.core.interpreter import RegexInterpreter
from rasa.core.interpreter import RasaNLUInterpreter
from slack import SlackInput
# import SLACK_DEV_TOKEN, SLACK_CLIENT_TOKEN, VERIFICATION_TOKEN
# load your agent
import logging
logging.basicConfig(level=logging.DEBUG)
nlu_interpreter = RasaNLUInterpreter('./models/nlu')
agent = Agent.load('./models/', interpreter=nlu_interpreter)
print('------------------')
print(agent.is_core_ready())
print('---------------------------')

input_channel = SlackInput(
    '',
    'random', slack_retry_reason_header='x-slack-retry-reason',
    slack_retry_number_header='x-slack-retry-num')


agent.handle_channels([input_channel], 5005, "/", )
print('test')
