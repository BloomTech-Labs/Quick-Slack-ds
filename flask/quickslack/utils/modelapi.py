import requests, json

url = 'http://model:8080/predict'

def get_pred(input_text):

    val = {'input_text': input_text}
    with requests.post(url, data=json.dumps(val)) as response:
        content = response.json()
    
    return content