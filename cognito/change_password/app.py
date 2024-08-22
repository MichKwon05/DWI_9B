import boto3
from botocore.exceptions import ClientError
import json
import os
from db_conection import get_secret, get_connection, handle_response

headers_cors = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': '*',
    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
}

region_name = 'us-east-1'


def lambda_handler(event, context):
    secrets = get_secret()
    body = json.loads(event.get('body', {}))
    email = body.get('email')

    client_id = secrets['client_id']

    if not email:
        return handle_response('Missing email', 'Invalid input', 400)

    client = boto3.client('cognito-idp', region_name=region_name)

    try:
        response = client.forgot_password(
            ClientId=client_id,
            Username=email
        )
    except ClientError as e:
        return handle_response(e, f'Error initiating forgot password: {str(e)}', 400)

    return {
        'statusCode': 200,
        'headers': headers_cors,
        'body': json.dumps({'message': 'Checa tu correo, código de verifiación enviado'})
    }


def handle_response(error, message, status_code):
    return {
        'statusCode': status_code,
        'headers': headers_cors,
        'body': json.dumps({
            'statusCode': status_code,
            'message': message,
            'error': str(error)
        })
    }
