import boto3
from botocore.exceptions import ClientError
from db_conection import get_secret, get_connection, handle_response
import json

headers_cors = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': '*',
    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
}


def lambda_handler(event, context):
    body = json.loads(event['body'])
    email = body['email']
    password = body['password']

    client = boto3.client('cognito-idp', region_name='us-east-1')

    try:
        response = client.initiate_auth(
            ClientId='your_cognito_app_client_id',
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': email,
                'PASSWORD': password
            }
        )
    except ClientError as e:
        return handle_response(e, f'Error during login: {str(e)}', 400)

    return {
        'statusCode': 200,
        'headers': headers_cors,
        'body': json.dumps({
            'access_token': response['AuthenticationResult']['AccessToken'],
            'id_token': response['AuthenticationResult']['IdToken'],
            'refresh_token': response['AuthenticationResult']['RefreshToken']
        })
    }
