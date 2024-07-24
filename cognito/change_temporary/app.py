import boto3
from botocore.exceptions import ClientError
import json
import os

headers_cors = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': '*',
    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
}

region_name = 'us-east-1'
user_pool_id = os.getenv('USER_POOL_ID')


def lambda_handler(event, context):
    body = json.loads(event['body'])
    email = body['email']
    temporary_password = body['temporary_password']
    new_password = body['new_password']

    client = boto3.client('cognito-idp', region_name=region_name)

    try:
        # Authenticate the user with the temporary password
        response = client.initiate_auth(
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': email,
                'PASSWORD': temporary_password
            },
            ClientId=os.getenv('CLIENT_ID')
        )

        # Use the authentication tokens to change the password
        access_token = response['AuthenticationResult']['AccessToken']
        client.change_password(
            PreviousPassword=temporary_password,
            ProposedPassword=new_password,
            AccessToken=access_token
        )

    except ClientError as e:
        return handle_response(e, f'Error changing temporary password: {str(e)}', 400)

    return {
        'statusCode': 200,
        'headers': headers_cors,
        'body': json.dumps({'message': 'Password changed successfully'})
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
