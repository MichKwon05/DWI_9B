import unittest
#from cognito.sign_up.app import lambda_handler, generate_temporary_password, insert_into_user, send_temporary_password_email
import json
import cognito.login.app import lambda_handler

"""mock_body = {
   'body': json.dumps({
       'email': '20213tn011@utez.edu.mx',
       'name': 'Rafael',
       'phone': '+777864321',
       'lastname': 'Rodríguez',
       'second_lastname': 'Trejo',
       'id_rol': 2,
       'status': True
    })
}"""
# cursor.execute(insert_query, (email, name, lastname, second_lastname, phone, 2, True))


class TestSignUpFunction(unittest.TestCase):
    def test_lambda_handler(self):
        result = lambda_handler(mock_body, None)
        print(result)