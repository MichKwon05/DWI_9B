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

        if event['httpMethod'] == 'GET':
            if not event.get('body'):
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'Missing body in the event'})
                }

            request_body = json.loads(event['body'])

            if 'id_user' not in request_body:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'Missing id_user in the body'})
                }

            user_id = request_body['id_user']

            with connection.cursor() as cursor:
                sql = "SELECT * FROM users WHERE id_user = %s"
                cursor.execute(sql, user_id)
                result = cursor.fetchone()

            if not result:
                return {
                    'statusCode': 404,
                    'body': json.dumps({'error': f'User with ID {user_id} not found'})
                }

            return {
                'statusCode': 200,
                'body': json.dumps(result)
            }

        elif event['httpMethod'] == 'PATCH':
            if not event.get('body'):
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'Missing body in the event'})
                }

            request_body = json.loads(event['body'])

            if 'id_user' not in request_body or 'status' not in request_body:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'Missing id_user or status in the body'})
                }

            user_id = request_body['id_user']
            new_status = request_body['status']

            with connection.cursor() as cursor:
                sql = "UPDATE users SET status = %s WHERE id_user = %s"
                cursor.execute(sql, (new_status, user_id))
                connection.commit()

            return {
                'statusCode': 200,
                'body': json.dumps(
                    {'message': f'Estado del usuario con ID {user_id} actualizado correctamente a {new_status}'}
                )
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
        if connection:
            connection.close()
