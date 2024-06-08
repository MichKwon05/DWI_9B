import json
import pymysql
from pymysql import DatabaseError


def lambda_handler(event, context):
    try:
        connection = pymysql.connect(
            host='bookify.c7k64au0krfa.us-east-2.rds.amazonaws.com',
            user='admin',
            password='quesadilla123',
            db='library',
        )
        user = json.loads(event['body'])
        with connection.cursor() as cursor:
            sql = """INSERT INTO users (name, lastname, second_lastname, email, password, phone, id_rol, status)
                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(sql, (
                user['name'], user['lastname'], user.get('second_lastname', None),
                user['email'], user['password'], user['phone'], user['id_rol'],
                user.get('status', True))
                           )
            connection.commit()

        return {
            'statusCode': 200,
            'body': json.dumps('User creado con éxito')
        }
    except pymysql.err.MySQLError as e:
        raise DatabaseError(f"Error en la base de datos: {e}")
    except Exception as e:

        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }