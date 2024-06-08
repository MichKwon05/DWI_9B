import json
import pymysql
from utils.database import conn, logger

def lambda_handler(event):
    try:
        if event['httpMethod'] == 'GET':
            book_id = event['pathParameters']['id']
            with conn.cursor() as cursor:
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
            with conn.cursor() as cursor:
                sql = "UPDATE books SET status = %s WHERE id_book = %s"
                cursor.execute(sql, (new_status, book_id))
                conn.commit()
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
    finally:
        conn.close()