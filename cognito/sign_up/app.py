import boto3
from botocore.exceptions import ClientError
from db_conection import get_secret, get_connection, handle_response
import json
import string
import random
import os

headers_cors = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': '*',
    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
}


def lambda_handler(event, context):
    body = json.loads(event['body'])
    email = body['email']
    password = body['password']
    phone = body['phone']

    password = generate_temporary_password()

    client = boto3.client('cognito-idp', region_name='us-east-1')

    try:
        response = client.admin_create_user(
            UserPoolId=os.getenv("USER_POOL_ID"),
            Username=email,
            UserAttributes=[
                {'Name': 'email', 'Value': email},
                {'Name': 'phone_number', 'Value': phone},
                {'Name': 'email_verified', 'Value': 'true'}
            ],
            TemporaryPassword=password,
            MessageAction='SUPPRESS'
        )

        client.admin_add_user_to_group(
            UserPoolId='your_user_pool_id',
            Username=email,
            GroupName='clients'
        )

        send_temporary_password_email(email, password)

    except ClientError as e:
        return handle_response(e, f'Error during registration: {str(e)}', 400)

    return {
        'statusCode': 200,
        'headers': headers_cors,
        'body': json.dumps({'message': 'User registered successfully'})
    }


def generate_temporary_password(length=12):
    special_characters = '^$*.[]{}()?-"!@#%&/\\,><\':;|_~`+= '
    characters = string.ascii_letters + string.digits + special_characters

    while True:
        password = ''.join(random.choice(characters) for _ in range(length))

        has_digit = any(char.isdigit() for char in password)
        has_upper = any(char.isupper() for char in password)
        has_lower = any(char.islower() for char in password)
        has_special = any(char in special_characters for char in password)

        if has_digit and has_upper and has_lower and has_special and len(password) >= 8:
            return password


def send_temporary_password_email(email, temp_password):
    ses_client = boto3.client('ses', region_name='us-east-1')
    subject = "Your Temporary Password"
    body_text = f"Hello,\n\nYour temporary password is: {temp_password}\n\nBest regards,\nYour Team"

    try:
        response = ses_client.send_email(
            Source='your_verified_email@example.com',
            Destination={
                'ToAddresses': [email]
            },
            Message={
                'Subject': {
                    'Data': subject
                },
                'Body': {
                    'Text': {
                        'Data': body_text
                    }
                }
            }
        )
        print("Email sent! Message ID:"),
        print(response['MessageId'])
    except ClientError as e:
        print(f"Error sending email: {e}")
