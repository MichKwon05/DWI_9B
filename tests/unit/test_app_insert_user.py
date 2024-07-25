import unittest
from cognito.sign_up.app import lambda_handler, generate_temporary_password, insert_into_user, send_temporary_password_email
import json
#from cognito.login.app import lambda_handler

mock_body = {
   'body': json.dumps({
       'email': '20213tn011@utez.edu.mx',
       'name': 'Andrea',
       'phone': '+7774622407',
       'lastname': 'Estrada',
       'second_lastname': 'Hernández',
       'id_rol': 2,
       'status': True
    })
}

mock_body_login = {
    'body': json.dumps({
        'email': '20213tn011@utez.edu.mx',
        'password': ';oh5Bkv5wjue'
    })
}
# cursor.execute(insert_query, (email, name, lastname, second_lastname, phone, 2, True))


class TestSignUpFunction(unittest.TestCase):
    def test_lambda_handler(self):
        result = lambda_handler(mock_body, None)
        print(result)