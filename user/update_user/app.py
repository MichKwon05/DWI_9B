import json
import boto3
from db_connection import get_secret, get_connection

headers_cors = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': '*',
    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
}


def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
    except (TypeError, KeyError, json.JSONDecodeError):
        return {
            'statusCode': 400,
            'headers': headers_cors,
            'body': json.dumps({'message': 'Invalid request body.'})
        }

    user_id = body.get('id_user')
    name = body.get('name')
    lastname = body.get('lastname')
    second_lastname = body.get('second_lastname')
    email = body.get('email')
    phone = body.get('phone')
    id_rol = body.get('id_rol')
    password = body.get('password')  # Only include if you want to allow updating passwords

    if not user_id or not name or not lastname or not email or not phone:
        return {
            'statusCode': 400,
            'headers': headers_cors,
            'body': json.dumps({'message': 'Missing required parameters.'})
        }

    try:
        connection = get_connection()
        response = update_user(user_id, name, lastname, second_lastname, email, phone, id_rol, password, connection)
        return response
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers_cors,
            'body': json.dumps({'message': f'An error occurred: {str(e)}'})
        }


def update_user(user_id, name, lastname, second_lastname, email, phone, id_rol, password, connection):
    try:
        with connection.cursor() as cursor:
            update_query = """
            UPDATE users
            SET name = %s,
                lastname = %s,
                second_lastname = %s,
                email = %s,
                phone = %s,
                id_rol = %s
            WHERE id_user = %s
            """
            params = (name, lastname, second_lastname, email, phone, id_rol, user_id)
            if password:  # Update password only if provided
                update_query += ", password = %s"
                params += (password,)

            cursor.execute(update_query, params)
            connection.commit()
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers_cors,
            'body': json.dumps({'message': f'An error occurred while updating the user: {str(e)}'})
        }
    finally:
        connection.close()

    return {
        'statusCode': 200,
        'headers': headers_cors,
        'body': json.dumps({'message': 'User updated successfully.'})
    }
