import json
from .db_connection import get_connection, handle_response
import pymysql

headers_cors = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': '*',
    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
}


def lambda_handler(event, context):
    connection = get_connection()
    if isinstance(connection, dict):  # Verificar si `get_connection` devolvió un error
        return connection

    try:
        body = json.loads(event.get('body', '{}'))
        book_id = body.get('id_book')
        new_status = body.get('status')

        if not book_id or new_status is None:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'ID del libro y estado son obligatorios.'})
            }

        with connection.cursor() as cursor:
            # Actualizar el estado del libro
            sql = "UPDATE books SET status = %s WHERE id_book = %s"
            cursor.execute(sql, (new_status, book_id))
            connection.commit()

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Estado del libro actualizado con éxito'})
        }

    except pymysql.err.MySQLError as e:
        return handle_response(e, f'Error en la base de datos: {str(e)}', 500)

    except Exception as e:
        return handle_response(e, f'Error en la operación: {str(e)}', 500)

    finally:
        connection.close()
