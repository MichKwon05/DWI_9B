import json
import pymysql
from .db_connection import get_connection, handle_response  # Asegúrate de importar correctamente

headers_cors = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': '*',
    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
}


def lambda_handler(event, context):
    connection = get_connection()
    if isinstance(connection, dict):  # Verificar si `get_connection` devolvió un error
        return connection

    books = []

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id_book, title, author, gener, year, description, synopsis, status FROM books")
            result = cursor.fetchall()

            for row in result:
                book = {
                    'id_book': row['id_book'],
                    'title': row['title'],
                    'author': row['author'],
                    'gener': row['gener'],
                    'year': row['year'],
                    'description': row['description'],
                    'synopsis': row['synopsis'],
                    'status': row['status'],
                    'images': [],
                    'pdfs': []
                }

                cursor.execute("SELECT url FROM images_books WHERE id_book = %s", (row['id_book'],))
                image_results = cursor.fetchall()
                for image_row in image_results:
                    book['images'].append(image_row['url'])

                cursor.execute("SELECT url FROM pdfs_books WHERE id_book = %s", (row['id_book'],))
                pdf_results = cursor.fetchall()
                for pdf_row in pdf_results:
                    book['pdfs'].append(pdf_row['url'])

                books.append(book)

    except pymysql.err.MySQLError as e:
        return handle_response(e, f'Error en la base de datos: {str(e)}', 500)

    except Exception as e:
        return handle_response(e, f'Error en la operación: {str(e)}', 500)

    finally:
        connection.close()

    return {
        "statusCode": 200,
        'headers': headers_cors,
        "body": json.dumps({
            'statusCode': 200,
            'message': 'Libros obtenidos correctamente',
            'data': books
        }),
    }
