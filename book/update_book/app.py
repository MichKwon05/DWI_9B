import json
from .db_connection import get_connection, handle_response
from requests_toolbelt.multipart import decoder
import base64
import cloudinary.uploader
import os
import pymysql

# Configuración de Cloudinary (solo necesario si se suben nuevos archivos)
cloudinary.config(
    cloud_name=os.getenv("cloud_name"),
    api_key=os.getenv("api_key"),
    api_secret=os.getenv("api_secret"),
    secure=True
)

headers_cors = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': '*',
    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
}


def upload_to_cloudinary(file, folder, resource_type="image"):
    upload_result = cloudinary.uploader.upload(file, folder=folder, resource_type=resource_type)
    return upload_result['secure_url']


def lambda_handler(event, context):
    connection = get_connection()
    if isinstance(connection, dict):  # Verificar si `get_connection` devolvió un error
        return connection

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
        book_id = None

        # Procesar cada parte del contenido multipart
        for part in multipart_data.parts:
            content_disposition = part.headers[b'Content-Disposition'].decode()
            name = content_disposition.split(';')[1].split('=')[1].strip('"')
            if name == 'id_book':
                book_id = int(part.text)
            elif name in ['title', 'author', 'genre', 'year', 'description', 'synopsis', 'status']:
                book_data[name] = part.text
            elif name == 'images':
                images.append(part.content)  # Obtener el contenido del archivo
            elif name == 'pdf':
                pdf_file = part.content  # Obtener el contenido del archivo

        if not book_id:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'ID del libro es obligatorio.'})
            }

        # Validar campos obligatorios
        required_fields = ['title', 'author', 'genre', 'year', 'description', 'synopsis']
        for field in required_fields:
            if field not in book_data:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': f'El campo {field} es obligatorio.'})
                }

        with connection.cursor() as cursor:
            # Actualizar los datos del libro en la base de datos
            update_fields = ', '.join([f"{key} = %s" for key in book_data.keys()])
            sql = f"UPDATE books SET {update_fields} WHERE id_book = %s"
            cursor.execute(sql, (*book_data.values(), book_id))

            # Subir y actualizar imágenes en Cloudinary
            cursor.execute("SELECT url FROM images_books WHERE id_book = %s", (book_id,))
            existing_images = cursor.fetchall()

            existing_image_urls = set(row['url'] for row in existing_images)
            new_image_urls = set()

            for image in images:
                cloudinary_url = upload_to_cloudinary(image, folder='imagebook', resource_type="image")
                new_image_urls.add(cloudinary_url)

                if cloudinary_url not in existing_image_urls:
                    sql = "INSERT INTO images_books (url, id_book) VALUES (%s, %s)"
                    cursor.execute(sql, (cloudinary_url, book_id))

            for url in existing_image_urls - new_image_urls:
                sql = "DELETE FROM images_books WHERE url = %s AND id_book = %s"
                cursor.execute(sql, (url, book_id))

            # Subir y actualizar el PDF en Cloudinary
            if pdf_file:
                cloudinary_pdf_url = upload_to_cloudinary(pdf_file, folder='pdfbook', resource_type="raw")
                cursor.execute("SELECT url FROM pdfs_books WHERE id_book = %s", (book_id,))
                existing_pdfs = cursor.fetchall()
                existing_pdf_urls = set(row['url'] for row in existing_pdfs)

                if cloudinary_pdf_url not in existing_pdf_urls:
                    sql = "INSERT INTO pdfs_books (url, id_book) VALUES (%s, %s)"
                    cursor.execute(sql, (cloudinary_pdf_url, book_id))

            connection.commit()

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Libro modificado con éxito'})
        }

    except pymysql.err.MySQLError as e:
        return handle_response(e, f'Error en la base de datos: {str(e)}', 500)

    except Exception as e:
        return handle_response(e, f'Error en la operación: {str(e)}', 500)

    finally:
        connection.close()
