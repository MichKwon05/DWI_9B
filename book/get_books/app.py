import json
import pymysql
import os
import boto3
from botocore.exceptions import ClientError
from typing import Dict
import logging


def lambda_handler(__):
    try:
        connection = pymysql.connect(
            host='bookify.c7k64au0krfa.us-east-2.rds.amazonaws.com',
            user='admin',
            password='quesadilla123',
            db='library',
            cursorclass=pymysql.cursors.DictCursor
        )
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM books")
            result = cursor.fetchall()
        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }
    except pymysql.MySQLError as e:
        print("ERROR: Could not retrieve events.")
        print(e)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Error retrieving events', 'message': str(e)})
        }
