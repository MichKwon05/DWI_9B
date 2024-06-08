import json
import pymysql
from utils.database import conn, logger

def lambda_handler(event):
    try:
        user_id = event('id_user')
        with conn.cursor() as cursor:
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
    finally:
        conn.close()