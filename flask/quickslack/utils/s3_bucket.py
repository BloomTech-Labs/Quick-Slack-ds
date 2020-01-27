import logging
import boto3
from botocore.exceptions import ClientError
from decouple import config

# ExtraArgs = json.loads(config('ExtraArgs'))

ExtraArgs = {
    "ACL":"public-read",
    "Metadata":{"mykey":"myvalue"},
    "ContentType": "image/png",
    "ContentDisposition": "inline"
}

AWS = {
    'aws_access_key_id': config('aws_access_key_id'),
    'aws_secret_access_key': config('aws_secret_access_key')
}

def upload_file(file_name, bucket, object_name=None):
    if object_name is None:
        object_name = file_name

    s3_client = boto3.client('s3', **AWS)

    response = s3_client.upload_file(file_name, bucket, object_name, ExtraArgs=ExtraArgs)
    # with open(file_name, "rb") as f:
    #     s3.upload_fileobj(f, bucket, object_name, ExtraArgs=ExtraArgs)
    return response