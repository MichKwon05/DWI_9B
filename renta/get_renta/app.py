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
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM rents")
            # Convertir resultados en una lista de diccionarios
            result = [dict(row) for row in cursor.fetchall()]

        # Convertir objetos date a cadenas de texto
        for row in result:
            row['initial_date'] = row['initial_date'].strftime('%Y-%m-%d')
            row['final_date'] = row['final_date'].strftime('%Y-%m-%d')

        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
