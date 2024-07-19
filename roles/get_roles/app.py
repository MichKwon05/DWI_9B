import json
from db_connection import get_connection, handle_response

headers_cors = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': '*',
    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
}


def lambda_handler(event, context):
    connection = get_connection()

    # Verifica si 'connection' es un diccionario, lo que indica un error
    if isinstance(connection, dict):
        return connection

    roles = []

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id_rol, name_rol, status FROM roles")
            result = cursor.fetchall()

            for row in result:
                role = {
                    'id_rol': row[0],
                    'name_rol': row[1],
                    'status': row[2]
                }
                roles.append(role)

    except Exception as e:
        return handle_response(str(e), 'Error al obtener roles.', 500)

    finally:
        connection.close()

    return {
        "statusCode": 200,
        'headers': headers_cors,
        "body": json.dumps({
            'statusCode': 200,
            'message': 'get roles',
            'data': roles
        }),
    }
