import os
import slack

client = slack.WebClient('xoxb-919411570391-907405094641-QgxzzwzbMI3VIftdRp3uLfCm')

response = client.chat_postMessage(
    channel='#random',
    text="<@Owen> <:fireball:> <:fireball:> <:fireball:>  THE VISION <:fireball:> <:fireball:> <:fireball:>")
assert response["ok"]
assert response["message"]["text"] == "Hello world!"