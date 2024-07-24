import boto3
from botocore.exceptions import ClientError
import json
import jwt
import requests
import os

headers_cors = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': '*',
    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
}

client_id = os.getenv("CLIENT_ID")
user_pool_id = os.getenv("USER_POOL_ID")


def lambda_handler(event, context):
    body = json.loads(event['body'])
    email = body['email']
    password = body['password']

    client = boto3.client('cognito-idp', region_name='us-east-1')

    try:
        response = client.initiate_auth(
            ClientId=client_id,
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': email,
                'PASSWORD': password
            }
        )
    except ClientError as e:
        return handle_response(e, f'Error during login: {str(e)}', 400)

    id_token = response['AuthenticationResult']['IdToken']

    # Decode and verify the JWT
    try:
        public_keys = get_public_keys()
        decoded_token = verify_jwt(id_token, public_keys)
        if not decoded_token:
            raise ValueError('Invalid JWT token')
    except Exception as e:
        return handle_response(e, f'Error decoding JWT: {str(e)}', 400)

    return {
        'statusCode': 200,
        'headers': headers_cors,
        'body': json.dumps({
            'access_token': response['AuthenticationResult']['AccessToken'],
            'id_token': id_token,
            'refresh_token': response['AuthenticationResult']['RefreshToken']
        })
    }


def get_public_keys():
    keys_url = f'https://cognito-idp.us-east-1.amazonaws.com/{user_pool_id}/.well-known/jwks.json'
    response = requests.get(keys_url)
    keys = response.json()['keys']
    return {key['kid']: key for key in keys}


def verify_jwt(token, public_keys, algorithms=['RS256']):
    headers = jwt.get_unverified_headers(token)
    key = public_keys.get(headers['kid'])
    if not key:
        raise ValueError('Public key not found')
    try:
        decoded = jwt.decode(token, key, algorithms=algorithms)
        return decoded
    except jwt.ExpiredSignatureError:
        raise ValueError('Token expired')
    except jwt.InvalidTokenError:
        raise ValueError('Invalid token')


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
