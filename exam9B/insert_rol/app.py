import json
import pymysql
import os
from pymysql import DatabaseError

def lambda_handler(event, context):
    try:
        connection = pymysql.connect(
            host=os.environ['DB_HOST'],
            user=os.environ['DB_USER'],
            password=os.environ['DB_PASSWORD'],
            db=os.environ['DB_NAME'],
            cursorclass=pymysql.cursors.DictCursor
        )
        rol_data = json.loads(event['body'])
        name_rol = rol_data['name_rol']
        status = rol_data.get('status', True)
        try:
            with connection.cursor() as cursor:
                sql = "INSERT INTO roles (name_rol, status) VALUES (%s, %s)"
                cursor.execute(sql, (name_rol, status))
                connection.commit()
        except pymysql.MySQLError as e:
            print(f"Error: {e}")
            return {
                'statusCode': 500,
                'body': json.dumps('Error creating role')
            }
        finally:
            connection.close()

        return {
            'statusCode': 200,
            'body': json.dumps('Rol creado con éxito')
        }
    except pymysql.err.MySQLError as e:
        raise DatabaseError(f"Error en la base de datos: {e}")
    except Exception as e:

        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
    finally:
        if connection:
            connection.close()
