import json
import pymysql
import os


def lambda_handler(event, context):
    # Conexión a la base de datos
    try:
        connection = pymysql.connect(
            host=os.getenv('DATABASE_HOST', 'localhost'),
            user=os.getenv('DATABASE_USER', 'root'),
            password=os.getenv('DATABASE_PASSWORD', 'root'),
            db=os.getenv('DATABASE_NAME', 'library'),
            cursorclass=pymysql.cursors.DictCursor
        )

        renta_id = event['pathParameters']['id']

        with connection.cursor() as cursor:
            sql = "UPDATE rents SET status=FALSE WHERE id_rents=%s"
            cursor.execute(sql, (renta_id,))
        connection.commit()

        response = {
            'statusCode': 200,
            'body': json.dumps({'message': 'Renta finalizada con éxito'})
        }
    except KeyError as e:
        response = {
            'statusCode': 400,
            'body': json.dumps({'message': f'Error: Falta el parámetro "id" en el evento: {str(e)}'})
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
