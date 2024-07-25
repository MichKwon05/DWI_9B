import json
import pymysql
import cloudinary
import cloudinary.uploader
from requests_toolbelt.multipart import decoder
import base64
import os
try:
    from db_connection import get_secret, get_connection, handle_response
except ImportError:
    from .db_connection import get_secret, get_connection, handle_response

# Configuración de Cloudinary
cloudinary.config(
    cloud_name=os.getenv("cloud_name"),
    api_key=os.getenv("api_key"),
    api_secret=os.getenv("api_secret"),
    secure=True
)


def upload_to_cloudinary(file, folder, resource_type="image"):
    upload_result = cloudinary.uploader.upload(file, folder=folder, resource_type=resource_type)
    return upload_result['secure_url']


def lambda_handler(event, context):
    try:
        # Verificar si el cuerpo está codificado en Base64 y decodificarlo
        if 'isBase64Encoded' in event and event['isBase64Encoded']:
            body = base64.b64decode(event["body"])
        else:
            body = event["body"]

        # Obtener el tipo de contenido del encabezado
        content_type = event['headers'].get('Content-Type') or event['headers'].get('content-type')
        if not content_type:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Content-Type header is missing'})
            }

        # Decodificar los datos multipart
        multipart_data = decoder.MultipartDecoder(body, content_type)
        book_data = {}
        images = []
        pdf_file = None

        # Procesar cada parte del contenido multipart
        for part in multipart_data.parts:
            content_disposition = part.headers[b'Content-Disposition'].decode()
            name = content_disposition.split(';')[1].split('=')[1].strip('"')
            if name in ['title', 'author', 'genre', 'year', 'description', 'synopsis', 'status']:
                book_data[name] = part.text
            elif name == 'images':
                images.append(part.content)  # Obtener el contenido del archivo
            elif name == 'pdf':
                pdf_file = part.content  # Obtener el contenido del archivo

        # Validar que se proporcionen entre 1 y 3 imágenes
        if len(images) < 1 or len(images) > 3:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Debe proporcionar entre 1 y 3 imágenes.'})
            }

        # Validar campos obligatorios
        required_fields = ['title', 'author', 'genre', 'year', 'description', 'synopsis']
        for field in required_fields:
            if field not in book_data:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': f'El campo {field} es obligatorio.'})
                }

        # Conectar a la base de datos
        connection = get_connection()
        if isinstance(connection, dict):  # Verificar si `get_connection` devolvió un error
            return connection

        try:
            with connection.cursor() as cursor:
                # Insertar los datos del libro en la base de datos
                sql = """INSERT INTO books (title, author, genre, year, description, synopsis, status)
                         VALUES (%s, %s, %s, %s, %s, %s, %s)"""
                cursor.execute(sql, (
                    book_data['title'], book_data['author'], book_data['genre'], book_data['year'],
                    book_data['description'], book_data['synopsis'], book_data.get('status', True))
                               )
                book_id = cursor.lastrowid

                # Subir y registrar las imágenes en Cloudinary
                for image in images:
                    cloudinary_url = upload_to_cloudinary(image, folder='imagebook', resource_type="image")
                    sql = "INSERT INTO images_books (url, id_book) VALUES (%s, %s)"
                    cursor.execute(sql, (cloudinary_url, book_id))

                # Subir y registrar el PDF en Cloudinary
                if pdf_file:
                    cloudinary_pdf_url = upload_to_cloudinary(pdf_file, folder='pdfbook', resource_type="raw")
                    sql = "INSERT INTO pdfs_books (url, id_book) VALUES (%s, %s)"
                    cursor.execute(sql, (cloudinary_pdf_url, book_id))

                connection.commit()

            return {
                'statusCode': 200,
                'body': json.dumps({'message': 'Libro creado con éxito'})
            }

        except pymysql.err.MySQLError as e:
            return handle_response(e, f'Error en la base de datos: {str(e)}', 500)

        except Exception as e:
            return handle_response(e, f'Error en la operación: {str(e)}', 500)

        finally:
            connection.close()

    except Exception as e:
        return handle_response(e, f'Error en la operación: {str(e)}', 500)
