import os
import unittest

os.environ['DATABASE_URL'] = 'sqlite:///:memory:'

from app import app, db


class EndToEndFlowTest(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        with self.app.app_context():
            db.drop_all()
            db.create_all()

    def test_signup_login_create_sop_and_answer_question(self):
        signup_resp = self.client.post('/auth/signup', json={
            'email': 'user@example.com',
            'password': 'secret123'
        })
        self.assertEqual(signup_resp.status_code, 201)

        login_resp = self.client.post('/auth/login', json={
            'email': 'user@example.com',
            'password': 'secret123'
        })
        self.assertEqual(login_resp.status_code, 200)
        token = login_resp.get_json()['access_token']
        self.assertTrue(token)

        create_resp = self.client.post('/sops/', json={
            'title': 'Incident SOP',
            'content': 'Follow the incident response steps carefully and escalate if the issue is critical.',
            'department_name': 'IT'
        }, headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(create_resp.status_code, 201)

        list_resp = self.client.get('/sops/', headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(list_resp.status_code, 200)
        self.assertEqual(len(list_resp.get_json()), 1)

        question_resp = self.client.post('/questions/', json={
            'sop_id': create_resp.get_json()['id'],
            'question': 'What should I do if the issue is critical?'
        }, headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(question_resp.status_code, 200)
        self.assertIn('answer', question_resp.get_json())

        history_resp = self.client.get('/answers/', headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(history_resp.status_code, 200)
        self.assertEqual(len(history_resp.get_json()), 1)


if __name__ == '__main__':
    unittest.main()
