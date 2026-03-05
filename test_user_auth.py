import unittest
from app import app, db
from models import User

class UserAuthTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = app.test_client()
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_register_success(self):
        response = self.client.post('/api/register', json={
            "first_name": "Test",
            "last_name": "User",
            "email": "test@example.com",
            "national_id": "1234567890123",
            "date_of_birth": "1990-01-01",
            "phone_number": "0801234567",
            "password": "password123"
        })
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertTrue(data['success'])

    def test_register_duplicate_email(self):
        self.client.post('/api/register', json={
            "first_name": "Test1",
            "last_name": "User1",
            "email": "duplicate@example.com",
            "national_id": "1111111111111",
            "date_of_birth": "1990-01-01",
            "phone_number": "0801234567",
            "password": "password123"
        })
        response = self.client.post('/api/register', json={
            "first_name": "Test2",
            "last_name": "User2",
            "email": "duplicate@example.com",
            "national_id": "2222222222222",
            "date_of_birth": "1990-01-01",
            "phone_number": "0801234567",
            "password": "password123"
        })
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], "Email already exists")

    def test_login_success(self):
        self.client.post('/api/register', json={
            "first_name": "Login",
            "last_name": "User",
            "email": "login@example.com",
            "idCard": "3333333333333",
            "dob": "1990-01-01",
            "phone": "0801112222",
            "password": "password123"
        })
        response = self.client.post('/api/login', json={
            "identifier": "0801112222",
            "password": "password123"
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        
        # Test with national ID too
        response = self.client.post('/api/login', json={
            "identifier": "3333333333333",
            "password": "password123"
        })
        self.assertEqual(response.status_code, 200)

    def test_update_profile(self):
        self.client.post('/api/register', json={
            "first_name": "Old",
            "last_name": "Name",
            "email": "update@example.com",
            "idCard": "4444444444444",
            "dob": "1990-01-01",
            "phone": "0801234567",
            "password": "password123"
        })
        # Login to get session
        self.client.post('/api/login', json={
            "identifier": "0801234567",
            "password": "password123"
        })
        # Update
        response = self.client.put('/api/user/profile', json={
            "first_name": "New",
            "phone_number": "0999999999"
        })
        self.assertEqual(response.status_code, 200)
        
        # Verify db manually within app context just to be sure
        with app.app_context():
            user = User.query.filter_by(email="update@example.com").first()
            self.assertEqual(user.first_name, "New")
            self.assertEqual(user.phone_number, "0999999999")

if __name__ == '__main__':
    unittest.main()
