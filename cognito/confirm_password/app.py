import boto3
from botocore.exceptions import ClientError
import json
import os

headers_cors = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': '*',
    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
}

client_id = os.getenv('CLIENT_ID')
region_name = 'us-east-1'


def lambda_handler(event, context):
    body = json.loads(event.get('body', {}))
    email = body.get('email')
    confirmation_code = body.get('confirmation_code')
    new_password = body.get('new_password')

    if not email or not confirmation_code or not new_password:
        return handle_response('Missing parameters', 'Invalid input', 400)

    client = boto3.client('cognito-idp', region_name=region_name)

    try:
        response = client.confirm_forgot_password(
            ClientId=client_id,
            Username=email,
            ConfirmationCode=confirmation_code,
            Password=new_password
        )
    except ClientError as e:
        return handle_response(e, f'Error confirming forgot password: {str(e)}', 400)

    return {
        'statusCode': 200,
        'headers': headers_cors,
        'body': json.dumps({'message': 'Password has been reset successfully'})
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
