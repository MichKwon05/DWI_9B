import json
from utils.database import conn, logger
import pymysql

def lambda_handler():
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM books")
            result = cursor.fetchall()
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
