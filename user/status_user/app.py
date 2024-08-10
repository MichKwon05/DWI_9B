import json
import jwt
import requests
from jwt import PyJWKClient
from db_connetion import get_secret, get_connection, handle_response

headers_cors = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': '*',
    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
}


def lambda_handler(event, context):
    # Autorización JWT
    auth_header = event.get('headers', {}).get('Authorization', '')
    if not auth_header:
        return {
            'statusCode': 401,
            'headers': headers_cors,
            'body': json.dumps({"error": "No token provided"})
        }

    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != 'bearer':
        return {
            'statusCode': 401,
            'headers': headers_cors,
            'body': json.dumps({"error": "Invalid authorization header format"})
        }

    token = parts[1]

    secrets = get_secret()
    region = 'us-east-1'
    user_pool_id = secrets['user_pool_id']
    client_id = secrets['client_id']
    keys_url = f'https://cognito-idp.{region}.amazonaws.com/{user_pool_id}/.well-known/jwks.json'

    try:
        response = requests.get(keys_url)
        response.raise_for_status()
        jwk_client = PyJWKClient(keys_url)
        signing_key = jwk_client.get_signing_key_from_jwt(token)
        decoded_token = jwt.decode(token, signing_key.key, algorithms=['RS256'], audience=client_id)

        if decoded_token.get('iss') != f'https://cognito-idp.{region}.amazonaws.com/{user_pool_id}':
            return handle_response('Invalid issuer', 'Unauthorized', 401)

        user_roles = decoded_token.get('cognito:groups', [])

        if 'Admins' not in user_roles:
            return handle_response('Forbidden', 'You do not have permission to access this resource', 403)

    except jwt.ExpiredSignatureError:
        return handle_response('Token expired', 'Unauthorized', 401)
    except jwt.InvalidTokenError:
        return handle_response('Invalid token', 'Unauthorized', 401)
    except requests.exceptions.RequestException as e:
        return handle_response(str(e), 'Error fetching JWK keys', 500)
    except Exception as e:
        return handle_response(str(e), 'Error verifying token', 500)

    # Procesamiento del cuerpo de la solicitud
    try:
        body = json.loads(event['body'])
    except (TypeError, KeyError, json.JSONDecodeError):
        return {
            'statusCode': 400,
            'headers': headers_cors,
            'body': json.dumps({'message': 'Invalid request body.'})
        }

    user_id = body.get('id_user')
    status = body.get('status')

    if user_id is None or status is None:
        return {
            'statusCode': 400,
            'headers': headers_cors,
            'body': json.dumps({'message': 'Faltan parámetros'})
        }

    if not isinstance(status, bool):
        return {
            'statusCode': 400,
            'headers': headers_cors,
            'body': json.dumps({'message': 'Status must be a boolean.'})
        }

    try:
        connection = get_connection()
        user_exists = check_user_exists(user_id, connection)
        if not user_exists:
            return {
                'statusCode': 404,
                'headers': headers_cors,
                'body': json.dumps({'message': 'Usuario no encontrado'})
            }
        response = update_user_status(user_id, status, connection)
        return response
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers_cors,
            'body': json.dumps({'message': f'An error occurred: {str(e)}'})
        }


def check_user_exists(id_user, connection):
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) FROM users WHERE id_user = %s",
                (id_user,)
            )
            result = cursor.fetchone()
            return result[0] > 0
    except Exception as e:
        raise e


def update_user_status(user_id, status, connection):
    try:
        with connection.cursor() as cursor:
            update_query = """
            UPDATE users
            SET status = %s
            WHERE id_user = %s
            """
            cursor.execute(update_query, (status, user_id))
            connection.commit()
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers_cors,
            'body': json.dumps({'message': f'Error al actualizar el status: {str(e)}'})
        }
    finally:
        connection.close()

    return {
        'statusCode': 200,
        'headers': headers_cors,
        'body': json.dumps({'message': 'Estado cambiado correctamente'})
    }
