import boto3
from botocore.exceptions import ClientError
from db_conection import handle_response
import json
import os

headers_cors = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': '*',
    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
}


def lambda_handler(event, context):
    body = json.loads(event['body'])
    email = body['email']
    new_password = body['new_password']

    client = boto3.client('cognito-idp', region_name='us-east-1')

    try:
        response = client.admin_set_user_password(
            UserPoolId=os.getenv("USER_POOL_ID"),
            Username=email,
            Password=new_password,
            Permanent=True
        )
    except ClientError as e:
        return handle_response(e, f'Error changing temporary password: {str(e)}', 400)

    return {
        'statusCode': 200,
        'headers': headers_cors,
        'body': json.dumps({'message': 'Password changed successfully'})
    }
