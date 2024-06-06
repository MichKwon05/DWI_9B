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
    book_data = json.loads(event['body'])
    title = book_data['title']
    author = book_data['author']
    gener = book_data['gener']
    year = book_data['year']
    description = book_data['description']
    synopsis = book_data['synopsis']
    date_register = book_data['data_register']
    status = book_data['status']

    # Subir image a S3
    image_file = book_data['image_file']
    image_key = f"images/{title}_{author}_image.jpg"
    s3_client.put_object(
        Body=image_file,
        Bucket=os.environ['aws-sam-cli-managed-default-samclisourcebucket-x4zrnk6sfupj'],
        Key=image_key
    )
    image_url = f"https://{os.environ['aws-sam-cli-managed-default-samclisourcebucket-x4zrnk6sfupj']}.s3.amazonaws.com/{image_key}"

    # Subir PDF a S3
    pdf_file = book_data['pdf_file']
    pdf_key = f"pdfs/{title}_{author}_pdf.pdf"
    s3_client.put_object(
        Body=pdf_file,
        Bucket=os.environ['aws-sam-cli-managed-default-samclisourcebucket-x4zrnk6sfupj'],
        Key=pdf_key
    )
    pdf_url = f"https://{os.environ['aws-sam-cli-managed-default-samclisourcebucket-x4zrnk6sfupj']}.s3.amazonaws.com/{pdf_key}"

    connection = connect()
    with connection.cursor() as cursor:
        sql = """INSERT INTO books (title, author, gener, year, description, synopsis, date_register, image_url, pdf_url, status)
                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE)"""
        cursor.execute(sql, title, author, gener, year, description, synopsis, date_register, image_url, pdf_url,
                       status)
        connection.commit()
    return {
        'statusCode': 200,
        'body': json.dumps('Libro created successfully')
    }
