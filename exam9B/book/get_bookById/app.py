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
        book_id = event['pathParameters']['id_book']
        with connection.cursor() as cursor:
            sql = "SELECT * FROM books WHERE id_book = %s"
            cursor.execute(sql, book_id)
            result = cursor.fetchone()
        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
    finally:
        connection.close()