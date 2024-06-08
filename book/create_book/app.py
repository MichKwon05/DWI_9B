import json
import pymysql
import os
import boto3
from botocore.exceptions import ClientError
from typing import Dict
import logging

s3_client = boto3.client('s3')


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

    try:
        connection = pymysql.connect(
            host='bookify.c7k64au0krfa.us-east-2.rds.amazonaws.com',
            user='admin',
            password='quesadilla123',
            db='library',
        )

        with connection.cursor() as cursor:
            sql = """INSERT INTO books (title, author, gener, year, description, synopsis, date_register, image_url, pdf_url, status)
                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(sql,
                           (title, author, gener, year,
                            description, synopsis, date_register, image_url, pdf_url, status))
            connection.commit()

        return {
            'statusCode': 200,
            'body': json.dumps('Libro creado exitosamente')
        }
    except pymysql.MySQLError as e:
        print("ERROR: Could not retrieve events.")
        print(e)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Error retrieving events', 'message': str(e)})
        }


def get_secret(secret_name: str, region_name: str) -> Dict[str, str]:
    """
    Retrieves the secret value from AWS Secrets Manager.

    Args:
        secret_name (str): The name or ARN of the secret to retrieve.
        region_name (str): The AWS region where the secret is stored.

    Returns:
        dict: The secret value retrieved from AWS Secrets Manager.
    """
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager', region_name=region_name)

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        logging.error("Failed to retrieve secret: %s", e)
        raise e

    return json.loads(get_secret_value_response['SecretString'])
