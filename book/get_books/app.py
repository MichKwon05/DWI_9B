import json
import pymysql
from pymysql import DatabaseError

def lambda_handler(event, context):

    connection = pymysql.connect(
        host='bookify.c7k64au0krfa.us-east-2.rds.amazonaws.com',
        user='admin',
        password='quesadilla123',
        db='library',
    )

    try:

        books = []
        with connection.cursor() as cursor:
            cursor.execute("SELECT id_book, title, author , gener , year, description , synopsis FROM books")
            result = cursor.fetchall()

            for row in result:
                books = {
                    'id': row[0],
                    'title': row[1],
                    'author': row[2],
                    'year': row[3],
                    'description': row[4]
                }

        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }
    except pymysql.err.MySQLError as e:
        raise DatabaseError(f"Error en la base de datos: {e}")

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

    finally:
        connection.close()
