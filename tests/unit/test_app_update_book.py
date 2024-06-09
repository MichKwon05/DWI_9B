from book.update_book import app


def test_lambda_handler():
    mock = {
        "id_book": 1,
        "title": "Princesas",
        "author": "Mich",
        "gener": "drama",
        "year": "2003",
        "description": "abonos semanales",
        "synopsis": "Este es un libro que  habla de todo",
        "status": 1
    }
    app.lambda_handler(mock, None)
    assert False
