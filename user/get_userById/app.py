import json
from .db_connection import get_connection, handle_response, execute_query

headers_cors = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': '*',
    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
}


def lambda_handler(event, context):
    id_user = None

    if 'queryStringParameters' in event:
        id_user = event['queryStringParameters'].get('id_user')
    if not id_user and 'body' in event:
        body = json.loads(event.get('body', '{}'))
        id_user = body.get('id_user')

    if not id_user:
        return handle_response(None, 'Falta un parámetro.', 400)

    connection = None
    try:
        connection = get_connection()
        query = """SELECT id_user, name, lastname, second_lastname, id_cognito, email, password, phone, id_rol, status
                   FROM users WHERE id_user = %s"""
        result = execute_query(connection, query, (id_user,))

        if result:
            user = {
                'id_user': result[0][0],
                'name': result[0][1],
                'lastname': result[0][2],
                'second_lastname': result[0][3],
                'id_cognito': result[0][4],
                'email': result[0][5],
                'password': result[0][6],
                'phone': result[0][7],
                'id_rol': result[0][8],
                'status': result[0][9]
            }
            return {
                'statusCode': 200,
                'headers': headers_cors,
                'body': json.dumps({
                    'statusCode': 200,
                    'message': 'Información del usuario obtenida correctamente.',
                    'data': user
                })
            }
        else:
            return handle_response(None, 'Usuario no encontrado', 404)
    except Exception as e:
        return handle_response(e, 'Ocurrió un error al obtener el usuario', 500)
    finally:
        if connection:
            connection.close()
