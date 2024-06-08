import json
import pymysql


def lambda_handler(event, context):
    try:

        connection = pymysql.connect(
            host='bookify.c7k64au0krfa.us-east-2.rds.amazonaws.com',
            user='admin',
            password='quesadilla123',
            db='library',
        )
        user = json.loads(event['body'])
        user_id = event['pathParameters']['id_user']

        with connection.cursor() as cursor:
            sql = """UPDATE users SET name = %s, last_name = %s, second_lastname = %s, email = %s, password = %s, phone = %s, id_rol = %s, status = %s WHERE id_user = %s"""
            cursor.execute(sql, (
                user['name'], user['last_name'], user.get('second_lastname', None), user['email'], user['password'],
                user['phone'], user['id_rol'], user['status'], user_id))
            connection.commit()

        return {
            'statusCode': 200,
            'body': json.dumps('Usuario modificado correctamente')
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
