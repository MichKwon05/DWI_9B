import json
import boto3
from .db_conection import get_secret, calculate_secret_hash


def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
    except (TypeError, KeyError, json.JSONDecodeError):
        return {
            'statusCode': 400,
            'body': 'Invalid request body.'
        }

    email = body.get('email')
    old_password = body.get('old_password')
    new_password = body.get('new_password')

    try:
        secret = get_secret()
        response = change_password(email, old_password, new_password, secret)
        return response
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f'An error occurred: {str(e)}')
        }


def change_password(email, old_password, new_password, secret):
    global client
    try:
        client = boto3.client('cognito-idp')
        secret_hash = calculate_secret_hash(secret['COGNITO_CLIENT_ID'], secret['SECRET_KEY'], email)

        response = client.change_password(
            PreviousPassword=old_password,
            ProposedPassword=new_password,
            AccessToken=None  # You can use AccessToken if you have it already
        )

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Password changed successfully'})
        }
    except client.exceptions.NotAuthorizedException as e:
        return {
            'statusCode': 400,
            'body': json.dumps('Old password does not match.')
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f'An error occurred: {str(e)}')
        }
