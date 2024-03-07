import requests
import unittest

bank_url = 'http://localhost:8000'
get_clients_url = f'{bank_url}/get_clients'
get_client_by_id = f'{bank_url}/get_client_by_id'
add_client_url = f'{bank_url}/add_client'
update_client_currency_url = f'{bank_url}/update_client_currency'
update_client_balance_url = f'{bank_url}/update_client_balance'
delete_client_url = f'{bank_url}/delete_client'
exchange_url = 'http://localhost:8001'
convert_currency_id_url = f'{exchange_url}/get_movie_by_id'

new_client = {
    "id": 0,
    "name": "testName",
    "currency": "RUB",
    "amount": 1000,
}


class TestComponent(unittest.TestCase):

    def test_1_add_client(self):
        res = requests.post(f"{add_client_url}", json=new_client)
        self.assertEqual(res.status_code, 200)

    def test_2_get_clients(self):
        res = requests.get(f"{get_clients_url}").json()
        self.assertTrue(new_client in res)

    def test_3_get_client_by_id(self):
        res = requests.get(f"{get_client_by_id}?client_id=0").json()
        self.assertEqual(res, new_client)

    def test_4_update_client_currency(self):
        res = requests.post(f"{update_client_currency_url}?client_id=0&new_currency=USD").json()
        self.assertEqual(res, "Currency updated successfully")

    def test_5_update_client_balance(self):
        res = requests.post(f"{update_client_balance_url}?client_id=0&amount=10").json()
        self.assertEqual(res, "Balance updated successfully")

    def test_6_delete_client(self):
        res = requests.delete(f"{delete_client_url}?client_id=0").json()
        self.assertEqual(res, "Success")


if __name__ == '__main__':
    unittest.main()
