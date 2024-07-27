import boto3
from botocore.exceptions import ClientError
import json

from jwt.algorithms import RSAAlgorithm

try:
    from db_conection import get_secret, get_connection, handle_response
except ImportError:
    from .db_conection import get_secret, get_connection, handle_response
import jwt
import requests
import os

headers_cors = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': '*',
    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
}


def lambda_handler(event, __):
    secrets = get_secret()
    client_id = secrets['client_id']
    user_pool_id = secrets['user_pool_id']
    client = boto3.client('cognito-idp', region_name='us-east-1')

    try:
        body_parameters = json.loads(event["body"])
        email = body_parameters.get('email')
        password = body_parameters.get('password')

        response = client.initiate_auth(
            ClientId=client_id,
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': email,
                'PASSWORD': password
            }
        )

        id_token = response['AuthenticationResult']['IdToken']
        access_token = response['AuthenticationResult']['AccessToken']
        refresh_token = response['AuthenticationResult']['RefreshToken']

        user_groups = client.admin_list_groups_for_user(
            Username=email,
            UserPoolId=user_pool_id  # Reemplaza las credenciales
        )

        role = None
        if user_groups['Groups']:
            role = user_groups['Groups'][0]['GroupName']  # Asumiendo un usuario pertenece a un solo grupo

        return {
            'statusCode': 200,
            'body': json.dumps({
                'id_token': id_token,
                'access_token': access_token,
                'refresh_token': refresh_token,
                'role': role
            })
        }
    except ClientError as e:
        return {
            'statusCode': 400,
            'body': json.dumps({"error": e.response['Error']['Message']})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({"error": str(e)})
        }


