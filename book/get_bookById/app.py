import json
import pymysql

def lambda_handler(event):

    try:
        connection = pymysql.connect(
            host='bookify.c7k64au0krfa.us-east-2.rds.amazonaws.com',
            user='admin',
            password='quesadilla123',
            db='library',
            cursorclass=pymysql.cursors.DictCursor
        )
        book_id = event('id_book')
        with connection.cursor() as cursor:
            sql = "SELECT * FROM books WHERE id_book = %s"
            cursor.execute(sql, book_id)
            result = cursor.fetchone()
        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }
    except pymysql.MySQLError as e:
        print("ERROR: Could not retrieve events.")
        print(e)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Error retrieving events', 'message': str(e)})
        }
    finally:
        connection.close()

