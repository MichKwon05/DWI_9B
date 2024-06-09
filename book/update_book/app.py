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
        if not event.get('body'):
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing body in the event'})
            }

        book = json.loads(event['body'])

        if 'id_book' not in book:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing id_book in the body'})
            }

        book_id = book['id_book']

        with connection.cursor() as cursor:
            sql = """UPDATE books SET title = %s, author = %s, gener = %s, year = %s, description = %s, synopsis = %s, status = %s WHERE id_book = %s"""
            cursor.execute(sql, (
                book['title'], book['author'], book['gener'], book['year'],
                book['description'], book['synopsis'], book.get('status', True), book_id))
            connection.commit()

        return {
            'statusCode': 200,
            'body': json.dumps('Book updated successfully')
        }
    except pymysql.err.MySQLError as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f"Database error: {e}"})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
    finally:
        if connection:
            connection.close()
