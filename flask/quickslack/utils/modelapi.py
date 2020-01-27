import requests, json
from decouple import config

def get_pred(input_text):

    val = {'input_text': input_text}
    with requests.post(config('MODEL_URL'), data=json.dumps(val)) as response:
        content = response.json()
    
    return content