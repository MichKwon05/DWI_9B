import json
import pymysql
import os
import boto3
from utils.database import conn, logger

s3_client = boto3.client('s3')

# import requests
def lambda_handler(event):
    book = json.loads(event['body'])
    book_id = event['pathParameters']['id_book']
    with conn.cursor() as cursor:
        sql = """UPDATE books SET title = %s, author = %s, gener = %s, year = %s, description = %s, synopsis = %s, image_url = %s, pdf_url = %s,  status = %s WHERE id_book = %s"""
        cursor.execute(sql, (
            book['title'], book['author'], book['gener'], book['year'],
            book['description'], book['synopsis'], book['image_url'], book['pdf_url'], book['status'], book_id))
        conn.commit()
    return {
        'statusCode': 200,
        'body': json.dumps('Usuario updated successfully')
    }
