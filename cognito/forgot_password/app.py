import json
import boto3
from db_conection import get_secret


def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
    except (TypeError, KeyError, json.JSONDecodeError):
        return {
            'statusCode': 400,
            'body': 'Invalid request body.'
        }

    email = body.get('email')

    try:
        secret = get_secret()
        response = forgot_password(email, secret)
        return response
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f'An error occurred: {str(e)}')
        }


def forgot_password(email, secret):
    global client
    try:
        client = boto3.client('cognito-idp')

        response = client.forgot_password(
            ClientId=secret['COGNITO_CLIENT_ID'],
            Username=email
        )

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Code sent successfully'})
        }
    except client.exceptions.UserNotFoundException as e:
        return {
            'statusCode': 404,
            'body': json.dumps('User not found.')
        }
    except client.exceptions.InvalidParameterException as e:
        return {
            'statusCode': 400,
            'body': json.dumps('Invalid email format.')
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f'An error occurred: {str(e)}')
        }
