import requests, json, time

if __name__ == "__main__":
    import urllib
    from PIL import Image
    import pickle
    from torchvision import transforms
    url, filename = ("https://github.com/pytorch/hub/raw/master/dog.jpg", "dog.jpg")
    try: urllib.URLopener().retrieve(url, filename)
    except: urllib.request.urlretrieve(url, filename)

    input_image = Image.open(filename)
    preprocess = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    input_tensor = preprocess(input_image)
    input_batch = input_tensor.unsqueeze(0)

    data = {
        "input_img": input_batch.detach().cpu().numpy().tolist()
    }

    headers = {
        "content-type": "application/json",
        "postman-token": "f7fb6e3f-26ba-a742-4ab3-03c953cefaf5"
    }
    body = {
        "signature_name": "predict_images",
        "inputs": data
    }
    now = time.time()
    json_response = requests.post(
        'http://tf-serving:8501/v1/models/resnet18:predict',
        data=json.dumps(body),
        headers=headers
    )

    print(f'EXEC TIME: {time.time()-now}')
    print(json_response.text)