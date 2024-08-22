import json
from db_connection import get_secret, get_connection, handle_response

headers_cors = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': '*',
    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
}


def lambda_handler(event, context):
    email = event.get('queryStringParameters', {}).get('email')

    if not email:
        return handle_response(None, 'Email parameter is missing', 400)

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM users WHERE email = %s"
            cursor.execute(sql, (email,))
            user = cursor.fetchone()

            if user:
                user_data = {
                    'id_user': user[0],
                    'name': user[1],
                    'lastname': user[2],
                    'second_lastname': user[3],
                    'email': user[4],
                    'password': user[5],
                    'phone': user[6],
                    'id_rol': user[7],
                    'status': user[8]
                }
                return {
                    'statusCode': 200,
                    'headers': headers_cors,
                    'body': json.dumps(user_data)
                }
            else:
                return handle_response(None, 'User not found', 404)

    except Exception as e:
        return handle_response(e, 'Failed to retrieve user', 500)
    finally:
        connection.close()
