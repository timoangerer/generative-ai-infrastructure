import asyncio
import time
from typing import Optional
import pulsar
import json
from pulsar.schema import Record, JsonSchema
import boto3
from io import BytesIO
from PIL import Image
import requests


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


def can_upload_to_s3(bucket_name, aws_region='eu-west-1'):
    # Create a Boto3 client for IAM
    iam_client = boto3.client('iam')

    try:
        # Simulate the policy for the current user
        response = iam_client.simulate_principal_policy(
            PolicySourceArn=f'arn:aws:iam::{aws_region}:user/example-user',
            ActionNames=['s3:PutObject'],
            ResourceArns=[f'arn:aws:s3:::{bucket_name}/*']
        )

        # Check if the user has the necessary permissions
        for result in response.get('EvaluationResults', []):
            if result.get('EvalDecision') == 'allowed':
                return True
            else:
                return False

    except Exception as e:
        return False


def is_pulsar_topic_available(service_url, topic):
    client = pulsar.Client(service_url)
    try:
        # Try to create a producer to check write access
        producer = client.create_producer(topic)
        producer.close()

        # Try to create a consumer to check read access
        subscription_name = 'test-subscription'
        consumer = client.subscribe(topic, subscription_name)
        consumer.close()

        return True
    except Exception as e:
        print(f"An error occurred: {e}")
        # Depending on the nature of the exception, you can determine
        # whether it's a read or write issue or both
        return False
    finally:
        client.close()


def is_possible_to_generate_txt2img(sd_server_url: str):
    try:
        response = requests.get(f"{sd_server_url}/app_id")

        if response.status_code == 200:
            return True
        else:
            return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False


async def all_functions_return_true(functions):
    async def safe_execution(fn):
        try:
            return await fn
        except Exception:
            raise ValueError("A function has thrown an error.")

    tasks = [safe_execution(fn) for fn in functions]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    if any(isinstance(result, Exception) for result in results):
        raise ValueError("One or more functions have thrown an error.")

    if all(results):
        return True
    else:
        raise ValueError("One or more functions have returned false.")


async def run_with_retries(function, max_retries, initial_delay):
    retry_count = 0
    delay = initial_delay
    last_exception: Optional[Exception] = None

    while retry_count < max_retries:
        try:
            return await function()
        except Exception as e:
            last_exception = e

            print(f"Error: {e}. Retrying...")
            retry_count += 1
            print(f"Retry {retry_count}/{max_retries} in {delay} seconds.")
            time.sleep(delay)
            delay *= 2  # Exponential backoff

    if last_exception is not None:
        raise last_exception
    else:
        raise Exception("An unknown error occurred.")
