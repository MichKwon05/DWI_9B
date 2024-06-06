import json
import pymysql
import os


def lambda_handler(event, context):
    try:
        connection = pymysql.connect(
            host=os.environ['DB_HOST'],
            user=os.environ['DB_USER'],
            password=os.environ['DB_PASSWORD'],
            db=os.environ['DB_NAME'],
            cursorclass=pymysql.cursors.DictCursor
        )
    except pymysql.MySQLError as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
    try:
        if event['httpMethod'] == 'GET':
            user_id = event['pathParameters']['id']
            with connection.cursor() as cursor:
                sql = "SELECT * FROM users WHERE id_user = %s"
                cursor.execute(sql, user_id)
                result = cursor.fetchone()
            return {
                'statusCode': 200,
                'body': json.dumps(result)
            }
        elif event['httpMethod'] == 'PATCH':
            user_id = event['pathParameters']['id']
            new_status = json.loads(event['body'])['status']
            # Aquí implementa la lógica para actualizar el estado del usuario
            return {
                'statusCode': 200,
                'body': json.dumps(
                    {'message': f'Estado del usuario con ID {user_id} actualizado correctamente a {new_status}'})
            }
        else:
            return {
                'statusCode': 405,
                'body': json.dumps({'error': 'Método HTTP no permitido'})
            }
    except KeyError as e:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': f'Parámetro faltante en la solicitud: {str(e)}'})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
    finally:
        connection.close()
