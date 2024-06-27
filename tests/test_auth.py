import unittest
from app import app

class AuthTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_register(self):
        response = self.app.post('/auth/register', json={
            'username': 'testuser',
            'password': 'testpass',
            'factory': 'testfactory'
        })
        self.assertEqual(response.status_code, 201)

    def test_login(self):
        self.app.post('/auth/register', json={
            'username': 'testuser',
            'password': 'testpass',
            'factory': 'testfactory'
        })
        response = self.app.post('/auth/login', json={
            'username': 'testuser',
            'password': 'testpass'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('access_token', response.get_json())

if __name__ == '__main__':
    unittest.main()
