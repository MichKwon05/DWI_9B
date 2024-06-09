import pymysql
import os
import json


def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
    except (TypeError, KeyError, json.JSONDecodeError):
        return {
            'statusCode': 400,
            'body': 'Invalid request body.'
        }

    title = body.get('title')
    author = body.get('author')
    genre = body.get('genre')
    year = body.get('year')
    description = body.get('description')
    synopsis = body.get('synopsis')
    date_register = body.get('date_register')
    status = body.get('status')
    image_urls = body.get('image_urls', [])
    pdf_urls = body.get('pdf_urls', [])


    if not title or not author or not genre or not year or not description or not synopsis or not date_register or not status:
        return {
            'statusCode': 400,
            'body': 'Missing parameters.'
        }

    try:
        year = int(year)
    except ValueError:
        return {
            'statusCode': 400,
            'body': 'Year must be an integer.'
        }

    try:
        date_register = str(date_register)  # Assuming it's already in proper format
    except ValueError:
        return {
            'statusCode': 400,
            'body': 'Date register must be a valid date string.'
        }

    response = insert_into_books(title, author, genre, year, description,
                                 synopsis, date_register, status, image_urls, pdf_urls)

    return response


def insert_into_books(title, author, genre, year, description, synopsis, date_register, status,
                      image_urls, pdf_urls):
    connection = pymysql.connect(
        host='bookify.c7k64au0krfa.us-east-2.rds.amazonaws.com',
        user='admin',
        password='quesadilla123',
        db='library',
    )

    try:
        with connection.cursor() as cursor:
            insert_query = """INSERT INTO books 
                              (title, author, genre, year, description, synopsis, date_register, status)  
                              VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(insert_query, (title, author, genre, year, description, synopsis, date_register, status))
            book_id = cursor.lastrowid

            for image_url in image_urls:
                insert_image_query = "INSERT INTO image_book (id_book, url) VALUES (%s, %s)"
                cursor.execute(insert_image_query, (book_id, image_url))

            for pdf_url in pdf_urls:
                insert_pdf_query = "INSERT INTO pdf_book (id_book, url) VALUES (%s, %s)"
                cursor.execute(insert_pdf_query, (book_id, pdf_url))

            connection.commit()

            connection.commit()

    except Exception as e:
        return {
            'statusCode': 500,
            'body': f'An error occurred: {str(e)}'
        }

    finally:
        connection.close()

    return {
        'statusCode': 200,
        'body': 'Record inserted successfully.'
    }
