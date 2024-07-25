import boto3
from botocore.exceptions import ClientError
import json
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
        try:
            body = json.loads(event['body'])
        except (TypeError, json.JSONDecodeError) as e:
            return handle_response(e, 'Error al analizar el cuerpo del evento.', 400)

        email = body.get('email')
        password = body.get('password')

        # Autenticación en Cognito
        response = client.initiate_auth(
            ClientId=client_id,
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': email,
                'PASSWORD': password
            }
        )

        # Verifica si 'AuthenticationResult' está en la respuesta
        if 'AuthenticationResult' not in response:
            raise ValueError('AuthenticationResult not found in response')

        id_token = response['AuthenticationResult']['IdToken']
        access_token = response['AuthenticationResult']['AccessToken']
        refresh_token = response['AuthenticationResult']['RefreshToken']

        # Verificación del JWT
        try:
            public_keys = get_public_keys()
            decoded_token = verify_jwt(id_token, public_keys)
            if not decoded_token:
                raise ValueError('Invalid JWT token')
        except Exception as e:
            return {
                'statusCode': 400,
                'body': json.dumps({"error_message": f'Error decoding JWT: {str(e)}'})
            }

        # Obtén los grupos del usuario
        user_groups = client.admin_list_groups_for_user(
            Username=email,
            UserPoolId=user_pool_id
        )

        # Determina el rol basado en el grupo
        role = None
        if user_groups['Groups']:
            role = user_groups['Groups'][0]['GroupName']  # Asumiendo un usuario pertenece a un solo grupo

        return {
            'statusCode': 200,
            'body': json.dumps({
                'id_token': id_token,
                'access_token': access_token,
                'refresh_token': refresh_token,
                'role': role,
                'response': response
            })
        }

    except ClientError as e:
        return {
            'statusCode': 400,
            'body': json.dumps({"error_message": e.response['Error']['Message']})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({"error_message": str(e)})
        }


def get_public_keys():
    secrets = get_secret()
    user_pool_id = secrets['user_pool_id']
    keys_url = f'https://cognito-idp.us-east-1.amazonaws.com/{user_pool_id}/.well-known/jwks.json'
    try:
        response = requests.get(keys_url)
        response.raise_for_status()
        keys = response.json()['keys']
        return {key['kid']: key for key in keys}
    except requests.RequestException as e:
        raise ValueError(f'Error retrieving public keys: {str(e)}')


def verify_jwt(token, public_keys, algorithms=['RS256']):
    unverified_headers = jwt.api_jws.get_unverified_header(token)
    kid = unverified_headers['kid']
    key = public_keys.get(kid)
    if not key:
        raise ValueError('Public key not found')
    try:
        decoded = jwt.decode(token, key, algorithms=algorithms)
        return decoded
    except jwt.ExpiredSignatureError:
        raise ValueError('Token expired')
    except jwt.InvalidTokenError:
        raise ValueError('Invalid token')
