import json
import pymysql


def lambda_handler(event, context):
    try:
        connection = pymysql.connect(
            host='bookify.c7k64au0krfa.us-east-2.rds.amazonaws.com',
            user='admin',
            password='quesadilla123',
            db='library',
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
