import json
import boto3
import pymysql
import os

s3_client = boto3.client('s3')
def connect():
    return pymysql.connect(
        host=rds_host,
        book=admin,
        passwd=admin123,
        db=db_name,
        connect_timeout=5
    )

def handler(event, context):
    http_method = event['httpMethod']
    if http_method == 'GET':
        if 'id_book' in event['pathParameters']:
            return get_book(event, context)
        else:
            return get_books(event, context)
    elif http_method == 'POST':
        return create_book(event, context)
    elif http_method == 'PUT':
        return update_book(event, context)
    elif http_method == 'DELETE':
        return delete_book(event, context)
    else:
        return {
            'statusCode': 405,
            'body': json.dumps('Method Not Allowed')
        }
def create_book(event, context):
    book_data = json.loads(event['body'])
    title = book_data['title']
    author = book_data['author']
    gener = book_data['gener']
    year = book_data['year']
    description = book_data['description']
    synopsis = book_data['synopsis']
    date_register = book_data['data_register']
    status =book_data['status']

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
        cursor.execute(sql, title, author, gener, year, description, synopsis, date_register, image_url, pdf_url, status)
        connection.commit()
    return {
        'statusCode': 200,
        'body': json.dumps('Libro created successfully')
    }

def get_books(event, context):
    connection = connect()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM books")
            result = cursor.fetchall()
    finally:
        connection.close()
    books_con_urls = []
    for book in result:
        book_con_url = {
            "id_book": book["id_book"],
            "title": book["title"],
            "author": book["author"],
            "gener": book["gener"],
            "year": book["year"],
            "description": book["description"],
            "synopsis": book["synopsis"],
            "date_register": book["date_register"],
            "image_url": f"https://{os.environ['S3_BUCKET_NAME']}.s3.amazonaws.com/images/{book['title']}_{book['author']}_image.jpg",
            "pdf_url": f"https://{os.environ['S3_BUCKET_NAME']}.s3.amazonaws.com/pdfs/{book['title']}_{book['author']}_pdf.pdf"
        }
        books_con_urls.append(book_con_url)
    return {
        'statusCode': 200,
        'body': json.dumps(books_con_urls)
    }

def get_book(event, context):
    connection = connect()
    book_id = event['pathParameters']['id_book']
    with connection.cursor() as cursor:
        sql = "SELECT * FROM books WHERE id_book = %s"
        cursor.execute(sql, book_id)
        result = cursor.fetchone()
    return {
        'statusCode': 200,
        'body': json.dumps(result)
    }

def update_book(event, context):
    connection = connect()
    book = json.loads(event['body'])
    book_id = event['pathParameters']['id_book']
    with connection.cursor() as cursor:
        sql = """INSERT INTO books (title, author, gener, year, description, synopsis, date_register, image_url, pdf_url, status)
                             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE)"""
        cursor.execute(sql, (book['title'], book['author'], book['gener'], book['year'], book['description'],
                             book['synopsis'], book['date_register'], book['image_url'], book['pdf_url'], book_id))
        connection.commit()
    return {
        'statusCode': 200,
        'body': json.dumps('Usuario updated successfully')
    }

def delete_book(event, context):
    connection = connect()
    book_id = event['pathParameters']['id_book']
    with connection.cursor() as cursor:
        sql = "DELETE FROM books WHERE id_book = %s"
        cursor.execute(sql, book_id)
        connection.commit()
    return {
        'statusCode': 200,
        'body': json.dumps('Book deleted successfully')
    }