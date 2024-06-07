import json
import pymysql
import os
from utils.database import conn, logger

def lambda_handler(event):
    try:

        renta_id = event('id')
        with conn.cursor() as cursor:
            sql = "UPDATE rents SET status=FALSE WHERE id_rents=%s"
            cursor.execute(sql, (renta_id,))
        conn.commit()

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
