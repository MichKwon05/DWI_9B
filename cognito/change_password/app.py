import boto3
from botocore.exceptions import ClientError
from db_conection import handle_response
import json

headers_cors = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': '*',
    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
}


def lambda_handler(event, context):
    body = json.loads(event['body'])
    username = body['username']
    new_password = body['new_password']

    client = boto3.client('cognito-idp', region_name='us-east-1')

    try:
        response = client.change_password(
            PreviousPassword=body['previous_password'],
            ProposedPassword=new_password,
            AccessToken=body['access_token']
        )
    except ClientError as e:
        return handle_response(e, f'Error updating password: {str(e)}', 400)

    return {
        'statusCode': 200,
        'headers': headers_cors,
        'body': json.dumps({'message': 'Password updated successfully'})
    }
