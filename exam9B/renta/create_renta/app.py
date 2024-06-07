import json
import pymysql
import os

def lambda_handler(event, context):
    # Conexión a la base de datos
    try:
        connection = pymysql.connect(
            host=os.getenv('DATABASE_HOST', 'localhost'),
            user=os.getenv('DATABASE_USER', 'root'),
            password=os.getenv('DATABASE_PASSWORD', 'osmich05'),
            db=os.getenv('DATABASE_NAME', 'library'),
            cursorclass=pymysql.cursors.DictCursor
        )
        # Obtener datos de la renta desde el cuerpo del evento
        renta = json.loads(event['body'])

        with connection.cursor() as cursor:
            sql = "INSERT INTO rents (initial_date, final_date, id_user, id_book) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (renta['initial_date'], renta['final_date'], renta['id_user'], renta['id_book']))
        connection.commit()

        response = {
            'statusCode': 200,
            'body': json.dumps({'message': 'Renta de libro almacenada correctamente'})
        }
    except KeyError as e:
        response = {
            'statusCode': 400,
            'body': json.dumps({'message': f'Error: Falta el parámetro en el cuerpo del evento: {str(e)}'})
        }
    except pymysql.MySQLError as e:
        response = {
            'statusCode': 500,
            'body': json.dumps({'message': f'Error de base de datos: {str(e)}'})
        }
    except Exception as e:
        response = {
            'statusCode': 500,
            'body': json.dumps({'message': f'Error inesperado: {str(e)}'})
        }
    finally:
        try:
            connection.close()
        except UnboundLocalError:
            pass  # Si connection nunca fue inicializada, no intentamos cerrarla

    return response
