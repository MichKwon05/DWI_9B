import json
import pymysql
import boto3
from botocore.exceptions import ClientError
from typing import Dict
from utils.database import conn, logger
import logging

def get_secret(secret_name: str, region_name: str) -> Dict[str, str]:
    """
    Retrieves the secret value from AWS Secrets Manager.

    Args:
        secret_name (str): The name or ARN of the secret to retrieve.
        region_name (str): The AWS region where the secret is stored.

    Returns:
        dict: The secret value retrieved from AWS Secrets Manager.
    """
    # Crear el cliente de Secrets Manager
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager', region_name=region_name)

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        logging.error("Failed to retrieve secret: %s", e)
        raise e

    return json.loads(get_secret_value_response['SecretString'])

def lambda_handler(event):
    secret_name = "dev/bookify/mysql"
    region_name = "us-east-1"

    try:
        secret = get_secret(secret_name, region_name)
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f"Failed to retrieve secret: {str(e)}"})
        }

    try:
        book_id = event('id_book')
        with conn.cursor() as cursor:
            sql = "SELECT * FROM books WHERE id_book = %s"
            cursor.execute(sql, book_id)
            result = cursor.fetchone()
        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }
    except pymysql.MySQLError as e:
        logger.error("ERROR: Could not retrieve events.")
        logger.error(e)
        return None  # Indicate error
    finally:
        conn.close()

