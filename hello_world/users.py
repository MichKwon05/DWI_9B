import json
import pymysql
import os

rds_host = os.environ['RDS_HOST']
name = os.environ['RDS_USERNAME']
password = os.environ['RDS_PASSWORD']
db_name = os.environ['RDS_DB_NAME']

def connect():
    return pymysql.connect(rds_host, user=name, passwd=password, db=db_name, connect_timeout=5)

def handler(event, context):
    http_method = event['httpMethod']
    if http_method == 'GET':
        if 'id_user' in event['pathParameters']:
            return get_user(event, context)
        else:
            return get_users(event, context)
    elif http_method == 'POST':
        return create_user(event, context)
    elif http_method == 'PUT':
        return update_user(event, context)
    elif http_method == 'DELETE':
        return delete_user(event, context)
    else:
        return {
            'statusCode': 405,
            'body': json.dumps('Method Not Allowed')
        }

def create_user(event, context):
    connection = connect()
    user = json.loads(event['body'])
    with connection.cursor() as cursor:
        sql = """INSERT INTO users (name, lastname, second_lastname, email, password, phone, id_rol, status)
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
        cursor.execute(sql, (user['name'], user['lastname'], user.get('second_lastname', None), user['email'], user['password'], user['phone'], user['id_rol'], user.get('status', True)))
        connection.commit()
    return {
        'statusCode': 200,
        'body': json.dumps('User created successfully')
    }

def get_users(event, context):
    connection = connect()
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM users")
        result = cursor.fetchall()
    return {
        'statusCode': 200,
        'body': json.dumps(result)
    }

def get_user(event, context):
    connection = connect()
    user_id = event['pathParameters']['id_user']
    with connection.cursor() as cursor:
        sql = "SELECT * FROM users WHERE id_user = %s"
        cursor.execute(sql, user_id)
        result = cursor.fetchone()
    return {
        'statusCode': 200,
        'body': json.dumps(result)
    }

def update_user(event, context):
    connection = connect()
    user = json.loads(event['body'])
    user_id = event['pathParameters']['id_user']
    with connection.cursor() as cursor:
        sql = """UPDATE users SET name = %s, last_name = %s, second_lastname = %s, email = %s, password = %s, phone = %s, id_rol = %s, status = %s WHERE id_user = %s"""
        cursor.execute(sql, (user['name'], user['last_name'], user.get('second_lastname', None), user['email'], user['password'], user['phone'], user['id_rol'], user['status'], user_id))
        connection.commit()
    return {
        'statusCode': 200,
        'body': json.dumps('Usuario updated successfully')
    }

def delete_user(event, context):
    connection = connect()
    user_id = event['pathParameters']['id_user']
    with connection.cursor() as cursor:
        sql = "DELETE FROM users WHERE id_user = %s"
        cursor.execute(sql, user_id)
        connection.commit()
    return {
        'statusCode': 200,
        'body': json.dumps('Usuario deleted successfully')
    }
