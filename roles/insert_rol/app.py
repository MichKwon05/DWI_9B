import json
import pymysql
import os
from pymysql import DatabaseError
from utils.database import conn, logger


def lambda_handler(event):
    try:
        rol_data = json.loads(event['body'])
        name_rol = rol_data['name_rol']
        status = rol_data.get('status', True)
        try:
            with conn.cursor() as cursor:
                sql = "INSERT INTO roles (name_rol, status) VALUES (%s, %s)"
                cursor.execute(sql, (name_rol, status))
                conn.commit()
        except pymysql.MySQLError as e:
            print(f"Error: {e}")
            return {
                'statusCode': 500,
                'body': json.dumps('Error creating role')
            }
        finally:
            conn.close()

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
        if conn:
            conn.close()
