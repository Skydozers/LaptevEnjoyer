import unittest
import psycopg2
from pathlib import Path
import asyncio
import sys

BASE_DIR = Path(__file__).resolve().parent

sys.path.append(str(BASE_DIR / 'bank_service/app'))
sys.path.append(str(BASE_DIR / 'exchange_service/app'))

from bank_service.app.main import service_alive as bank_status
from exchange_service.app.main import service_alive as exchange_status

class TestIntegration(unittest.TestCase):

    def test_database(self):
        try:
            conn = psycopg2.connect(
                dbname='Sypchenko',
                user='postgres',
                password='password',
                host='localhost',
                port='5432'
            )
            conn.close()
            check = True
        except Exception as e:
            check = False
        self.assertEqual(check, True)

    def test_bank_service_connection(self):
        r = asyncio.run(bank_status())
        self.assertEqual(r, {'message': 'service alive'})

    def test_exchange_service_connection(self):
        r = asyncio.run(exchange_status())
        self.assertEqual(r, {'message': 'service alive'})


if __name__ == '__main__':
    unittest.main()
