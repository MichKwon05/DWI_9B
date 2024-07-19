import json
from db_connection import get_connection, handle_response, execute_query, close_connection

headers_cors = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': '*',
    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
}


def lambda_handler(event, context):
    if 'queryStringParameters' in event:
        id_book = event['queryStringParameters'].get('id_book')
    else:
        body = json.loads(event.get('body', '{}'))
        id_book = body.get('id_book')

    if not id_book:
        return handle_response(None, 'Falta un parámetro.', 400)

    connection = get_connection()
    if isinstance(connection, dict):
        return connection

    query = f"SELECT id_book, title, author, gener, year, description, synopsis, status FROM books WHERE id_book = {id_book}"
    books = []

    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()

        for row in result:
            book = {
                'id_book': row[0],
                'title': row[1],
                'author': row[2],
                'gener': row[3],
                'year': row[4],
                'description': row[5],
                'synopsis': row[6],
                'status': row[8],
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

    except Exception as e:
        return handle_response(e, 'Ocurrió un error al obtener la información del libro:', 500)

    finally:
        close_connection(connection)

    return {
        'statusCode': 200,
        'headers': headers_cors,
        'body': json.dumps({
            'statusCode': 200,
            'message': 'Libro obtenido correctamente',
            'data': books
        })
    }
