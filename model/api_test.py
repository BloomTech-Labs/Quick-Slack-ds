import requests
import json

if __name__ == '__main__':
    url = 'http://127.0.0.1:8080/predict'
    # url = 'http://model-api:8080/predict'
    # url = 'http://0.0.0.0:8080/predict'
    input_text = 'Some people think the Earth is flat.'

    val = {'input_text': input_text}
    r_success = requests.post(url, data=json.dumps(val))

    print(f'request responded: {r_success}.')
    if r_success.status_code == 200:
        print(f'the content of the response was {r_success.json()}')
    else:
        print(r_success)