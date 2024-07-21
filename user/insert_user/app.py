import json
import boto3
from db_conection import get_secret, get_connection


def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
    except (TypeError, KeyError, json.JSONDecodeError):
        return {
            'statusCode': 400,
            'body': 'Invalid request body.'
        }

    password = body.get('password')
    email = body.get('email')
    name = body.get('name')
    lastname = body.get('lastname')
    second_lastname = body.get('second_lastname')
    phone = body.get('phone')
    id_rol = body.get('id_rol')

    if not password or not email or not name or not lastname or not phone or not id_rol:
        return {
            'statusCode': 400,
            'body': 'Missing parameters.'
        }

    try:
        secret = get_secret()
        response = register_user(email, password, name, lastname, second_lastname, phone, id_rol, secret)
        return response
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f'An error occurred: {str(e)}')
        }


def register_user(email, password, name, lastname, second_lastname, phone, id_rol, secret):
    try:
        client = boto3.client('cognito-idp')
        response = client.sign_up(
            ClientId=secret['COGNITO_CLIENT_ID'],
            Username=email,
            Password=password,
            UserAttributes=[
                {
                    'Name': 'email',
                    'Value': email
                },
                {
                    'Name': 'name',
                    'Value': name
                }
            ]
        )
        client.admin_add_user_to_group(
            UserPoolId=secret['COGNITO_USER_POOL_ID'],
            Username=email,
            GroupName=secret['COGNITO_GROUP_NAME']
        )

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f'An error occurred: {str(e)}')
        }

    insert_into_user(email, response['UserSub'], name, lastname, second_lastname, phone, id_rol, password)

    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
        },
        'body': json.dumps({'message': 'Send verification code', 'user': response['UserSub']})
    }


def insert_into_user(email, id_cognito, name, lastname, second_lastname, phone, id_rol, password):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            insert_query = """
            INSERT INTO users (email, id_cognito, name, lastname, second_lastname, phone, id_rol, password)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (email, id_cognito, name, lastname, second_lastname, phone, id_rol, password))
            connection.commit()

    except Exception as e:
        return {
            'statusCode': 500,
            'body': f'An error occurred: {str(e)}'
        }

    finally:
        connection.close()

    return {
        'statusCode': 200,
        'body': 'Record inserted successfully.'
    }


def verify_role(id_rol):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id_rol FROM roles WHERE id_rol = %s", (id_rol,))
            result = cursor.fetchone()
            return result is not None
    except Exception as e:
        return False
    finally:
        connection.close()
