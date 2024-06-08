import json
import pymysql
import os


def lambda_handler(event, __):
    try:
        connection = pymysql.connect(
            host='bookify.c7k64au0krfa.us-east-2.rds.amazonaws.com',
            user='admin',
            password='quesadilla123',
            db='library',
            cursorclass=pymysql.cursors.DictCursor
        )
        renta_id = event('id')
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
    return response
