from insert_user import app
import unittest


def test_lambda_handler():
    mock = {
        "body": {
            "nombre": "MAx",
            "ap_paterno": "Luna"
        }
    }
    app.lambda_handler(mock, None)
