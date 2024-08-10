import unittest
#from cognito.sign_up.app import lambda_handler, generate_temporary_password, insert_into_user
import json
#from cognito.login.app import lambda_handler
#from cognito.forgot_password.app import lambda_handler
#from cognito.change_temporary.app import lambda_handler
#from cognito.confirm_password.app import lambda_handler
#from cognito.sign_up.app import lambda_handler
#from cognito.log_out.app import lambda_handler
from user.get_users.app import lambda_handler

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
        'password': 'RafaRt22='
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
        'confirmation_code': '279120',
        'new_password': 'RafaRt22='
    })
}

token = "eyJraWQiOiJmdHdMUm5OWlFxM1lFd3pyNU5lZ3VJVW51d3hIazdsZ0VLeWtzUVg3aGJRPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiJiNDc4ZTQ1OC02MDExLTcwMjAtNjYyZC1jYzI1M2VkZWNkNzYiLCJjb2duaXRvOmdyb3VwcyI6WyJBZG1pbnMiXSwiZW1haWxfdmVyaWZpZWQiOmZhbHNlLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAudXMtZWFzdC0xLmFtYXpvbmF3cy5jb21cL3VzLWVhc3QtMV9YNlVhZmhxbGwiLCJjb2duaXRvOnVzZXJuYW1lIjoiYjQ3OGU0NTgtNjAxMS03MDIwLTY2MmQtY2MyNTNlZGVjZDc2Iiwib3JpZ2luX2p0aSI6IjJhOWY5Y2Y1LWIwYTAtNGIxYS1iMzk1LTAxMTUzNWY3NzJhYyIsImF1ZCI6Ijc3ZTJ1a3Q2aHJ0YjRiNjVsbjhzbzhidTY4IiwiZXZlbnRfaWQiOiI0OTQzYTRhZS04OGEwLTQ3OWEtOTg3YS01MjI2NzEwZDAyYzciLCJ0b2tlbl91c2UiOiJpZCIsImF1dGhfdGltZSI6MTcyMzI1MDYxMCwiZXhwIjoxNzIzMjU0MjEwLCJpYXQiOjE3MjMyNTA2MTAsImp0aSI6IjU5ZjBkNmY5LTEyODAtNDE4YS1iYWIxLTNmODk2YmQ3MzUxZCIsImVtYWlsIjoibWljaGVsbGVydWJpY2sxNUBnbWFpbC5jb20ifQ.Dl6zTOozCKO8CGIdGGA6lz_RFNx-Ol5F7VJ30wWE3uZIqYqAM4XG_jx8XGIk7MTaWVFvr3p-IsgBN1rO9LFfgTkTuh65dRblbAw1dCpNX68sqXdA87APDZdQoWJsG2A9IM49VcZPLAv1c9qjpIT5VhQthkr-btz1wwVrGaLEifFtDTlED47pakEylfMtdIupU0uAFoBwX0-N7ZnEjvN4egSxgTKzI4akCEsRw1dQ_C5FAfS8FqAhb5bhmON3zw5lLqL4M9n7M1dLXvTTIoQ79CJ_P676mjIByyy7qOzmH558tRsEBbmlMGpc4qsCSPXFavfTUQZhoVpAUhiMcfjDyw"
# Define el evento simulado
event = {
    "headers": {
        "Authorization": f"Bearer {token}"
    }
}

mock_logout = {
    'body': json.dumps({
        'access_token': 'eyJraWQiOiJzZmRhKzRZUjNTbWk3RGRTYVU4cTV0NTRaSW1sZnF1b003VHJZTXVvWlY4PSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiIyNDM4MzRmOC1kMDAxLTcwZGMtYWM1Yi1lZTNiYjBmZmNlZWQiLCJjb2duaXRvOmdyb3VwcyI6WyJDbGllbnRzIl0sImlzcyI6Imh0dHBzOlwvXC9jb2duaXRvLWlkcC51cy1lYXN0LTEuYW1hem9uYXdzLmNvbVwvdXMtZWFzdC0xX1g2VWFmaHFsbCIsImNsaWVudF9pZCI6Ijc3ZTJ1a3Q2aHJ0YjRiNjVsbjhzbzhidTY4Iiwib3JpZ2luX2p0aSI6ImQ1NGQyMWIyLWM0YmMtNDRhMi05ZTVhLWU5MTllZmE4ZDQwZiIsImV2ZW50X2lkIjoiY2YxMmM4NjAtZTIxOC00ZDA4LTg3NzItM2YyNzcyODczOTllIiwidG9rZW5fdXNlIjoiYWNjZXNzIiwic2NvcGUiOiJhd3MuY29nbml0by5zaWduaW4udXNlci5hZG1pbiIsImF1dGhfdGltZSI6MTcyMjEyOTEzNywiZXhwIjoxNzIyMTMyNzM3LCJpYXQiOjE3MjIxMjkxMzcsImp0aSI6ImFiYWFhYzQ2LTI4MzgtNGNlZS1hZmU3LTEwMTM4NGRhMmE4NyIsInVzZXJuYW1lIjoiMjQzODM0ZjgtZDAwMS03MGRjLWFjNWItZWUzYmIwZmZjZWVkIn0.QOQ9nU5ABaAsh7ufk6hkjyo8MpSxLaGPinoWLFIk_BKaXF0c3794Iub0GlVM7hXppU35CayK98ro2ZHAEf_EPx5MXbWETDHFKHmzg72ki2ovFknNbHYktdpAriG7rk9rsUhuP7AkrdM-AiNpMYV74B0_bveQMKaNHPcHRbJyR69eHEnfkSOOBZSvF4NZ7fPRcm5er9ZWxvEAUCW2oR9ht0qW1j87R4ywCKZie9hXT0ygqBorYrbwUT6KP_CKVJW_enjeHEXEADUIZz5zW170dTduBkWhXgUmBxAY3ftZ7RL2WSJvbX1LolHSAyg47h-9obVIeCiESWlmLNcbTyLV1g'
    })
}


class TestSignUpFunction(unittest.TestCase):
    def test_lambda_handler(self):
        result = lambda_handler(event, None)
        print(result)
