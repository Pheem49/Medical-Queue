import unittest
import json
from app import app, db
from models import Department

class DepartmentTestCase(unittest.TestCase):
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

    def test_get_empty_departments(self):
        response = self.client.get('/api/departments')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['departments'], [])

    def test_admin_create_department(self):
        response = self.client.post('/api/admin/departments', json={
            "name": "Cardiology"
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertIn('id', data)

        with app.app_context():
            dept = Department.query.get(data['id'])
            self.assertIsNotNone(dept)
            self.assertEqual(dept.name, "Cardiology")

    def test_admin_update_department(self):
        # First create a department
        post_response = self.client.post('/api/admin/departments', json={
            "name": "Neurology"
        })
        dept_id = post_response.get_json()['id']

        # Now update it
        put_response = self.client.put(f'/api/admin/departments/{dept_id}', json={
            "name": "Neurology Updated"
        })
        self.assertEqual(put_response.status_code, 200)
        data = put_response.get_json()
        self.assertTrue(data['success'])

        with app.app_context():
            dept = Department.query.get(dept_id)
            self.assertIsNotNone(dept)
            self.assertEqual(dept.name, "Neurology Updated")

    def test_get_departments(self):
        # Create a few departments
        self.client.post('/api/admin/departments', json={"name": "Dept A"})
        self.client.post('/api/admin/departments', json={"name": "Dept B"})

        response = self.client.get('/api/departments')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(len(data['departments']), 2)
        names = [d['name'] for d in data['departments']]
        self.assertIn("Dept A", names)
        self.assertIn("Dept B", names)

if __name__ == '__main__':
    unittest.main()
