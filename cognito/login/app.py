import boto3
from botocore.exceptions import ClientError
import json
try:
    from db_conection import get_secret, get_connection, handle_response
except ImportError:
    from .db_conection import get_secret, get_connection, handle_response
import jwt
from jwt import PyJWKClient

headers_cors = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': '*',
    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
}


def lambda_handler(event, __):
    secrets = get_secret()
    client_id = secrets['client_id']
    user_pool_id = secrets['user_pool_id']
    region = 'us-east-1'
    client = boto3.client('cognito-idp', region_name=region)

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

        jwk_url = f'https://cognito-idp.{region}.amazonaws.com/{user_pool_id}/.well-known/jwks.json'
        jwk_client = PyJWKClient(jwk_url)
        signing_key = jwk_client.get_signing_key_from_jwt(id_token)
        decoded_token = jwt.decode(id_token, signing_key.key, algorithms=['RS256'], audience=client_id)

        user_groups = decoded_token.get('cognito:groups', [])

        required_roles = ['Admins', 'Clients']

        if not any(role in user_groups for role in required_roles):
            return {
                'statusCode': 403,
                'body': json.dumps('Access denied: User does not have the required role')
            }

        return {
            'statusCode': 200,
            'body': json.dumps({
                'id_token': id_token,
                'access_token': access_token,
                'refresh_token': refresh_token,
                'role': user_groups
            }),
            'headers': headers_cors
        }

    except ClientError as e:
        return {
            'statusCode': 400,
            'body': json.dumps({"error": e.response['Error']['Message']}),
            'headers': headers_cors
        }
    except jwt.ExpiredSignatureError:
        return {
            'statusCode': 401,
            'body': json.dumps({"error": "Token expired"}),
            'headers': headers_cors
        }
    except jwt.InvalidTokenError:
        return {
            'statusCode': 401,
            'body': json.dumps({"error": "Invalid token"}),
            'headers': headers_cors
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({"error": str(e)}),
            'headers': headers_cors
        }

