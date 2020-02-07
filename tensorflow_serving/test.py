import requests, json, time

if __name__ == "__main__":
    data = json.dumps({
        "examples":[{"x": [5.1, 3.5, 1.4, 0.2]}]
    })

    headers = {
        "content-type": "application/json",
        "postman-token": "f7fb6e3f-26ba-a742-4ab3-03c953cefaf5"
    }
    now = time.time()
    json_response = requests.post('http://tf-serving:8501/v1/models/iris:classify', data=data, headers=headers)

    print(f'EXEC TIME: {time.time()-now}')
    print(json_response.text)