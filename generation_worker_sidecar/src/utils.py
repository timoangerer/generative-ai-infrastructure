import asyncio
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


class HealthCheckFailed(Exception):
    pass


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
        raise HealthCheckFailed(e)


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
        raise HealthCheckFailed(e)
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
        raise HealthCheckFailed(e)


async def retry_async_func(async_func, max_retries, initial_delay):
    attempt = 0
    delay = initial_delay

    while attempt < max_retries:
        try:
            return await async_func()
        except Exception as e:
            attempt += 1
            if attempt == max_retries:
                raise

            await asyncio.sleep(delay)

            delay *= 2

    # If somehow the loop exits without returning or raising (unlikely), explicitly raise an error
    raise RuntimeError(
        "Failed to complete the async operation despite retries.")


async def all_checks_successful(checks):
    async def factory_function():
        # Create new coroutine instances from check functions
        coroutines = [func() for func in checks]
        return await asyncio.gather(*coroutines, return_exceptions=False)

    await retry_async_func(factory_function, 3, 1)
    return True
