import requests

API_URL = 'https://your-api-id.execute-api.region.amazonaws.com/Prod'

def create_renta(renta):
    url = f'{API_URL}/create-renta'
    response = requests.post(url, json=renta)
    return response.json()

def delete_renta(renta_id):
    url = f'{API_URL}/delete-renta/{renta_id}'
    response = requests.delete(url)
    return response.json()

# Ejemplo de uso
if __name__ == "__main__":
    new_renta = {
        'initial_date': '2024-06-01',
        'final_date': '2024-06-10',
        'id_user': 1,
        'id_book': 1
    }
    print(create_renta(new_renta))

    print(delete_renta(1))
