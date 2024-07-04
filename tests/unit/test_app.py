from cognito.login import app
import unittest
import json

mock = {
    "body": json.dumps({
        "email": "20213tn011@utez.edu.mx",
        "password": "osmich05"
    })

}


class TestApp(unittest.TestCase):
    def test_lambda_handler(self):
        result = app.lambda_handler(mock, None)
        print(result)
        assert False
