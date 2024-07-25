import boto3
from botocore.exceptions import ClientError
import json
try:
    from db_conection import get_secret, get_connection, handle_response
except ImportError:
    from .db_conection import get_secret, get_connection, handle_response

headers_cors = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': '*',
    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
}


def lambda_handler(event, context):
    secrets = get_secret()
    client_id = secrets['client_id']
    try:
        body = json.loads(event['body'])
    except (TypeError, json.JSONDecodeError) as e:
        return handle_response(e, 'Error al analizar el cuerpo del evento.', 400)

    email = body.get('email')
    temporary_password = body.get('temporary_password')
    new_password = body.get('new_password')

    client = boto3.client('cognito-idp', region_name='us-east-1')

    try:
        # Authenticate the user with the temporary password
        response = client.initiate_auth(
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': email,
                'PASSWORD': temporary_password
            },
            ClientId=client_id
        )

        # Use the authentication tokens to change the password
        access_token = response['AuthenticationResult']['AccessToken']
        client.change_password(
            PreviousPassword=temporary_password,
            ProposedPassword=new_password,
            AccessToken=access_token
        )

    except ClientError as e:
        return handle_response(e, f'Error changing temporary password: {str(e)}', 400)

    return {
        'statusCode': 200,
        'headers': headers_cors,
        'body': json.dumps({'message': 'Password changed successfully'})
    }


def handle_response(error, message, status_code):
    return {
        'statusCode': status_code,
        'headers': headers_cors,
        'body': json.dumps({
            'statusCode': status_code,
            'message': message,
            'error': str(error)
        })
    }
