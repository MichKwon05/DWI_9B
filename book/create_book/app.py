import json
import pymysql
import cloudinary
import cloudinary.uploader
from pymysql import DatabaseError
from requests_toolbelt.multipart import decoder
import base64

# Configuración de Cloudinary
cloudinary.config(
    cloud_name="db5zuwucd",
    api_key="733776665585982",
    api_secret="UHMJ6N_YU8m5ozoxqyVKB68u49U",
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
        connection = pymysql.connect(
            host='bookify.c7k64au0krfa.us-east-2.rds.amazonaws.com',
            user='admin',
            password='quesadilla123',
            db='library',
        )
        try:
            with connection.cursor() as cursor:
                # Insertar los datos del libro en la base de datos
                sql = """INSERT INTO books (title, author, genre, year, description, synopsis, date_register, status)
                         VALUES (%s, %s, %s, %s, %s, %s, CURDATE(), %s)"""
                cursor.execute(sql, (
                    book_data['title'], book_data['author'], book_data['genre'], book_data['year'],
                    book_data['description'], book_data['synopsis'], book_data.get('status', True))
                               )
                book_id = cursor.lastrowid

                # Subir y registrar las imágenes en Cloudinary
                for image in images:
                    cloudinary_url = upload_to_cloudinary(image, folder='cover', resource_type="image")
                    sql = "INSERT INTO images_books (url, id_book) VALUES (%s, %s)"
                    cursor.execute(sql, (cloudinary_url, book_id))

                # Subir y registrar el PDF en Cloudinary
                if pdf_file:
                    cloudinary_pdf_url = upload_to_cloudinary(pdf_file, folder='files', resource_type="raw")
                    sql = "INSERT INTO pdfs_books (url, id_book) VALUES (%s, %s)"
                    cursor.execute(sql, (cloudinary_pdf_url, book_id))

                connection.commit()

            return {
                'statusCode': 200,
                'body': json.dumps({'message': 'Libro creado con éxito'})
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

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
