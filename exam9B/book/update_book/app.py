import json
import pymysql
import os
import boto3


def connect():
    return pymysql.connect(
        host="rds_host",
        book="admin",
        passwd="admin123",
        db="db_name",
        connect_timeout=5
    )


s3_client = boto3.client('s3')
# Configuración de la conexión a la base de datos
connection = pymysql.connect(
    host=os.environ['DB_HOST'],
    user=os.environ['DB_USER'],
    password=os.environ['DB_PASSWORD'],
    db=os.environ['DB_NAME'],
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)


# import requests
def lambda_handler(event, context):
    connection = connect()
    book = json.loads(event['body'])
    book_id = event['pathParameters']['id_book']
    with connection.cursor() as cursor:
        sql = """UPDATE books SET title = %s, author = %s, gener = %s, year = %s, description = %s, synopsis = %s, image_url = %s, pdf_url = %s,  status = %s WHERE id_book = %s"""
        cursor.execute(sql, (
            book['title'], book['author'], book['gener'], book['year'],
            book['description'], book['synopsis'], book['image_url'], book['pdf_url'], book['status'], book_id))
        connection.commit()
    return {
        'statusCode': 200,
        'body': json.dumps('Usuario updated successfully')
    }
    return {
        'statusCode': 200,
        'body': json.dumps('Usuario updated successfully')
    }
