# rol.py
import json
import pymysql
from db import connect

def create_rol(event, context):
    connection = connect()
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
        'body': json.dumps('Role created successfully')
    }

def get_roles(event, context):
    connection = connect()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM roles")
            result = cursor.fetchall()
    finally:
        connection.close()

    return {
        'statusCode': 200,
        'body': json.dumps(result)
    }

def get_rol(event, context):
    connection = connect()
    rol_id = event['pathParameters']['id_rol']
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM roles WHERE id_rol = %s"
            cursor.execute(sql, rol_id)
            result = cursor.fetchone()
    finally:
        connection.close()

    return {
        'statusCode': 200,
        'body': json.dumps(result)
    }

def update_rol(event, context):
    connection = connect()
    rol_data = json.loads(event['body'])
    rol_id = event['pathParameters']['id_rol']
    name_rol = rol_data['name_rol']
    status = rol_data['status']
    try:
        with connection.cursor() as cursor:
            sql = "UPDATE roles SET name_rol = %s, status = %s WHERE id_rol = %s"
            cursor.execute(sql, (name_rol, status, rol_id))
            connection.commit()
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps('Error updating role')
        }
    finally:
        connection.close()

    return {
        'statusCode': 200,
        'body': json.dumps('Role updated successfully')
    }

def delete_rol(event, context):
    connection = connect()
    rol_id = event['pathParameters']['id_rol']
    try:
        with connection.cursor() as cursor:
            sql = "DELETE FROM roles WHERE id_rol = %s"
            cursor.execute(sql, rol_id)
            connection.commit()
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps('Error deleting role')
        }
    finally:
        connection.close()

    return {
        'statusCode': 200,
        'body': json.dumps('Role deleted successfully')
    }
