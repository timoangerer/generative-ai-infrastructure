import json
from pulsar.schema import Record, JsonSchema
import boto3
from io import BytesIO
from PIL import Image


def convert_record_to_json(record_cls: Record, data: Record):
    jsonSchema = JsonSchema(record_cls)
    return json.loads(jsonSchema.encode(data))


def upload_image_to_s3(image: Image.Image, bucket_name: str, key: str):
    # Convert PIL image to bytes
    buffer = BytesIO()
    image.save(buffer, format='JPEG')
    image_bytes = buffer.getvalue()

    # Upload bytes to S3
    s3 = boto3.client('s3')
    s3.put_object(Bucket=bucket_name, Key=key, Body=image_bytes)
