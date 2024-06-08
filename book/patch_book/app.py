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

        if event['httpMethod'] == 'GET':
            book_id = event['pathParameters']['id']
            with connection.cursor() as cursor:
                sql = "SELECT * FROM books WHERE id_book = %s"
                cursor.execute(sql, book_id)
                result = cursor.fetchone()
            return {
                'statusCode': 200,
                'body': json.dumps(result)
            }
        elif event['httpMethod'] == 'PATCH':
            book_id = event['pathParameters']['id']
            new_status = json.loads(event['body'])['status']
            with connection.cursor() as cursor:
                sql = "UPDATE books SET status = %s WHERE id_book = %s"
                cursor.execute(sql, (new_status, book_id))
                connection.commit()
            return {
                'statusCode': 200,
                'body': json.dumps(
                    {'message': f'Estado del libro con ID {book_id} actualizado correctamente a {new_status}'})
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
