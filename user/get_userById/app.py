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
        user_id = event('id_user')
        with connection.cursor() as cursor:
            sql = "SELECT * FROM users WHERE id_user = %s"
            cursor.execute(sql, user_id)
            result = cursor.fetchone()
        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }