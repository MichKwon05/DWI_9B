import json
import pymysql

def lambda_handler():
    try:
        connection = pymysql.connect(
            host='bookify.c7k64au0krfa.us-east-2.rds.amazonaws.com',
            user='admin',
            password='quesadilla123',
            db='library',
            cursorclass=pymysql.cursors.DictCursor
        )
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users")
            result = cursor.fetchall()
        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
    finally:
        connection.close()
