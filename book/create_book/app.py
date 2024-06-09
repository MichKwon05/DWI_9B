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

        book = json.loads(event['body'])

        # Ejecutar la inserción del libro en la base de datos
        with connection.cursor() as cursor:
            sql = """INSERT INTO books (title, author, gener, year, description, synopsis, status)
                     VALUES (%s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(sql, (
                book['title'], book['author'], book['gener'], book['year'],
                book['description'], book['synopsis'], book.get('status', True))
                           )
            connection.commit()

        # Retornar una respuesta exitosa si todo está bien
        return {
            'statusCode': 200,
            'body': 'Libro creado con éxito'
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
