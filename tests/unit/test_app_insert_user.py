import unittest
#from cognito.sign_up.app import lambda_handler, generate_temporary_password, insert_into_user
import json
from cognito.login.app import lambda_handler
#from cognito.forgot_password.app import lambda_handler
#from cognito.change_temporary.app import lambda_handler
#from cognito.confirm_password.app import lambda_handler

mock_body = {
    'body': json.dumps({
        'email': '20213tn011@utez.edu.mx',
        'name': 'Andrea',
        'lastname': 'Estrada',
        'second_lastname': 'Hernández',
        'phone_number': '+7774622407',
        'id_rol': 2,
        'status': True
    })
}

mock_body_login = {
    'body': json.dumps({
        'email': '20213tn011@utez.edu.mx',
        'password': 'RafaRt20='
    })
}
# cursor.execute(insert_query, (email, name, lastname, second_lastname, phone, 2, True))

mock_forgot = {
    'body': json.dumps({
        'email': '20213tn011@utez.edu.mx',
    })
}

mock_temporary = {
    'body': json.dumps({
        'email': '20213tn011@utez.edu.mx',
        'temporary_password': 'Osmich05=',
        'new_password': 'OsmichKwon14='

    })
}

mock_confirm = {
    'body': json.dumps({
        'email': '20213tn011@utez.edu.mx',
        'confirmation_code': '690219',
        'new_password': 'RafaRt22='
    })
}


class TestSignUpFunction(unittest.TestCase):
    def test_lambda_handler(self):
        result = lambda_handler(mock_body_login, None)
        print(result)
