import json
import pymysql
import boto3

s3_client = boto3.client('s3')


def lambda_handler(event, context):
    connection = pymysql.connect(
        host='bookify.c7k64au0krfa.us-east-2.rds.amazonaws.com',
        user='admin',
        password='quesadilla123',
        db='library',
    )
    book = json.loads(event['body'])
    book_id = event['pathParameters']['id_book']
    with connection.cursor() as cursor:
        sql = """UPDATE books SET title = %s, author = %s, gener = %s, year = %s, description = %s, synopsis = %s, image_url = %s, pdf_url = %s,  status = %s WHERE id_book = %s"""
        cursor.execute(sql, (
            book['title'], book['author'], book['gener'], book['year'],
            book['description'], book['synopsis'], book['status'], book_id))
        connection.commit()
    return {
        'statusCode': 200,
        'body': json.dumps('Usuario updated successfully')
    }
