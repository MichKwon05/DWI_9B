import json
from db_connection import get_connection, handle_response

headers_cors = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': '*',
    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
}


def lambda_handler(event, context):
    connection = get_connection()

    books = []

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT b.id_book, b.title, b.author, b.gener, b.year, b.description, b.synopsis, b.date_register, b.image_url, b.pdf_url, b.status, "
                "i.url as image_url, i.mimeType as image_mimeType, i.fileBase64 as image_fileBase64, "
                "p.url as pdf_url, p.mimeType as pdf_mimeType, p.fileBase64 as pdf_fileBase64 "
                "FROM books b "
                "LEFT JOIN images_books i ON b.id_book = i.id_book "
                "LEFT JOIN pdfs_books p ON b.id_book = p.id_book"
            )
            result = cursor.fetchall()

            current_book = None
            for row in result:
                if current_book is None or current_book['id_book'] != row[0]:
                    current_book = {
                        'id_book': row[0],
                        'title': row[1],
                        'author': row[2],
                        'gener': row[3],
                        'year': row[4],
                        'description': row[5],
                        'synopsis': row[6],
                        'date_register': row[7],
                        'image_url': row[8],
                        'pdf_url': row[9],
                        'status': row[10],
                        'images': [],
                        'pdfs': []
                    }
                    if row[11]:  # If there's an image associated
                        current_book['images'].append({
                            'url': row[11],
                            'mimeType': row[12],
                            'fileBase64': row[13]
                        })
                    if row[14]:  # If there's a PDF associated
                        current_book['pdfs'].append({
                            'url': row[14],
                            'mimeType': row[15],
                            'fileBase64': row[16]
                        })
                    books.append(current_book)
                else:
                    # Same book, add additional images or pdfs if available
                    if row[11]:  # If there's an image associated
                        current_book['images'].append({
                            'url': row[11],
                            'mimeType': row[12],
                            'fileBase64': row[13]
                        })
                    if row[14]:  # If there's a PDF associated
                        current_book['pdfs'].append({
                            'url': row[14],
                            'mimeType': row[15],
                            'fileBase64': row[16]
                        })

    except Exception as e:
        return handle_response(str(e), 'Error al obtener libros.', 500)

    finally:
        connection.close()

    return {
        "statusCode": 200,
        'headers': headers_cors,
        "body": json.dumps({
            'statusCode': 200,
            'message': 'get books',
            'data': books
        }),
    }
