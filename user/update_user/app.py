import json
import pymysql


def lambda_handler(event, context):
    connection = pymysql.connect(
        host='bookify.c7k64au0krfa.us-east-2.rds.amazonaws.com',
        user='admin',
        password='quesadilla123',
        db='library',
    )

    try:
        if 'body' not in event or not event['body']:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing body in the event'})
            }

        user = json.loads(event['body'])

        if 'id_user' not in user:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing id_user in the body'})
            }

        user_id = user['id_user']

        with connection.cursor() as cursor:
            sql = """UPDATE users SET name = %s, lastname = %s, second_lastname = %s, email = %s, password = %s, phone = %s, id_rol = %s, status = %s WHERE id_user = %s"""
            cursor.execute(sql, (
                user['name'], user['lastname'], user.get('second_lastname', None), user['email'], user['password'],
                user['phone'], user['id_rol'], user['status'], user_id))
            connection.commit()

        return {
            'statusCode': 200,
            'body': json.dumps('Usuario modificado correctamente')
        }
    except pymysql.err.MySQLError as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f"Error en la base de datos: {e}"})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
    finally:
        if connection:
            connection.close()
