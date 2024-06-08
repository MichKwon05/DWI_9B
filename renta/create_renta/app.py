import json
import pymysql


def lambda_handler(event, context):
    try:
        connection = pymysql.connect(
            host='bookify.c7k64au0krfa.us-east-2.rds.amazonaws.com',
            user='admin',
            password='quesadilla123',
            db='library',
        )
        rents = json.loads(event['body'])

        with connection.cursor() as cursor:
            sql = "INSERT INTO rents (initial_date, final_date, id_user, id_book) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (rents['initial_date'], rents['final_date'], rents['id_user'], rents['id_book']))
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
    return response
