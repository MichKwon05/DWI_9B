import json
import jwt
import requests
from jwt import PyJWKClient
from db_connection import get_connection, handle_response, get_secret

headers_cors = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': '*',
    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
}


def lambda_handler(event, context):
    # Obtener el token del encabezado de autorización
    auth_header = event.get('headers', {}).get('Authorization', '')
    # Verificar que el encabezado no esté vacío
    if not auth_header:
        return {
            'statusCode': 401,
            'headers': headers_cors,
            'body': json.dumps({"error": "No token provided"})
        }

    # Suponiendo que el encabezado está en el formato "Bearer <token>"
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
        # Obtener claves JWK para verificar el token
        response = requests.get(keys_url)
        response.raise_for_status()  # Verifica que la solicitud se realizó correctamente
        keys = response.json()['keys']

        jwk_client = PyJWKClient(keys_url)
        signing_key = jwk_client.get_signing_key_from_jwt(token)
        decoded_token = jwt.decode(token, signing_key.key, algorithms=['RS256'], audience=client_id)

        # Verificar el emisor (iss) del token
        if decoded_token.get('iss') != f'https://cognito-idp.{region}.amazonaws.com/{user_pool_id}':
            return handle_response('Invalid issuer', 'Unauthorized', 401)

        # Obtener el rol del usuario desde el token decodificado
        user_roles = decoded_token.get('cognito:groups', [])

        # Verificar si el usuario tiene el rol adecuado para acceder a los usuarios
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

    id_user = None
    if 'queryStringParameters' in event and event['queryStringParameters'] is not None:
        id_user = event['queryStringParameters'].get('id_user')
    else:
        try:
            body = json.loads(event['body'])
        except (TypeError, json.JSONDecodeError) as e:
            return handle_response(e, 'Error al analizar el cuerpo del evento.', 400)
        id_user = body.get('id_user')

    if not id_user:
        return handle_response(None, 'Falta el id', 400)

    connection = get_connection()
    query = """
        SELECT id_user, name, lastname, second_lastname, email, password, phone, id_rol, status 
        FROM users 
        WHERE id_user = %s
    """
    user_data = []

    try:
        with connection.cursor() as cursor:
            cursor.execute(query, (id_user,))
            result = cursor.fetchall()

            #Si no hay datos no hay usuario
            if not result:
                return {
                    'statusCode': 404,
                    'headers': headers_cors,
                    'body': json.dumps({
                        'statusCode': 404,
                        'message': 'Usuario no encontrado.'
                    })
                }

            for row in result:
                user = {
                    'id_user': row[0],
                    'name': row[1],
                    'lastname': row[2],
                    'second_lastname': row[3],
                    'email': row[4],
                    'password': row[5],
                    'phone': row[6],
                    'id_rol': row[7],
                    'status': bool(row[8])
                }
                user_data.append(user)

    except Exception as e:
        return handle_response(e, 'Ocurrió un error al obtener la información del usuario.', 500)

    finally:
        connection.close()

    return {
        'statusCode': 200,
        'headers': headers_cors,
        'body': json.dumps({
            'statusCode': 200,
            'message': 'Información del usuario obtenida correctamente.',
            'data': user_data
        })
    }
