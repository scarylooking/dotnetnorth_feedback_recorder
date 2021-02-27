import json
import boto3
import uuid
import logging
import os
import utility

utility.configure_logger()


def lambda_handler(event, context):
    bucket_name = os.environ.get('bucket_name', None)

    if not environment_configured(bucket_name):
        return {'statusCode': 500}

    body = json.loads(event.get('body', '{}'))

    if not validate_request(body):
        return {'statusCode': 400}

    feedback_id = str(uuid.uuid4())

    if not write_feedback(bucket_name, feedback_id, body):
        return {'statusCode': 400}

    logging.info(f'successfully recorded feedback {feedback_id}')

    return {
        'statusCode': 200,
        'body': {
            'id': feedback_id
        },
        'headers': {
            'Content-Type': 'application/json',
            'x-powered-by': 'al.paca'
        }
    }


def validate_request(body):
    session = body.get('session', None)
    if session is None or not session:
        logging.error(f'Rejecting request because session parameter is missing or invalid: {session}')
        return False

    delivery = body.get('delivery', None)
    if delivery is None or not delivery:
        logging.error(f'Rejecting request because delivery parameter is missing or invalid: {delivery}')
        return False

    knowledge = body.get('knowledge', None)
    if knowledge is None or not knowledge:
        logging.error(f'Rejecting request because knowledge parameter is missing or invalid: {knowledge}')
        return False

    slides = body.get('slides', None)
    if slides is None or not slides:
        logging.error(f'Rejecting request because slides parameter is missing or invalid: {slides}')
        return False

    overall = body.get('overall', None)
    if overall is None or not overall:
        logging.error(f'Rejecting request because overall parameter is missing or invalid: {overall}')
        return False

    technical = body.get('technical', None)
    if slides is None or not slides:
        logging.error(f'Rejecting request because technical parameter is missing or invalid: {technical}')
        return False

    return True


def write_feedback(bucket_name: str, feedback_id: str, required_parameters: list):
    payload = {
        'id': feedback_id,
        'session': required_parameters['session'],
        'delivery': required_parameters['delivery'],
        'knowledge': required_parameters['knowledge'],
        'slides': required_parameters['slides'],
        'technical': required_parameters['technical'],
        'comments': required_parameters['comments'],
    }

    file_name = f'form/{feedback_id}.json'
    logging.info(f'writing feedback form to s3://{bucket_name}/{file_name}')

    try:
        s3 = get_s3_client()
        s3.put_object(Body=(bytes(json.dumps(payload).encode('UTF-8'))), Bucket=bucket_name, Key=file_name)
    except Exception as e:
        logging.error(f'failed to write feedback form {feedback_id} due to an exception: {str(e)}')
        return False

    return True


def get_s3_client():
    return boto3.client('s3')


def environment_configured(bucket_name: str):
    if bucket_name is None or not bucket_name:
        logging.error(f'bucket_name is not set')
        return False

    aws_key = os.environ.get('aws_access_key_id', None)
    if aws_key is None or not aws_key:
        logging.error(f'aws_key is not set')
        return False

    aws_secret = os.environ.get('aws_secret_access_key', None)

    if aws_secret is None or not aws_secret:
        logging.error(f'aws_secret is not set')
        return False

    return True
