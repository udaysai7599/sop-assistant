import io
import os
import unittest

os.environ['DATABASE_URL'] = 'sqlite:///:memory:'

from app import app, db


class DocumentWorkflowTest(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        with self.app.app_context():
            db.drop_all()
            db.create_all()

    def test_upload_and_query_document(self):
        signup_resp = self.client.post('/auth/signup', json={
            'email': 'admin2@example.com',
            'password': 'secret123',
            'admin_secret': 'change-me-in-production'
        })
        self.assertEqual(signup_resp.status_code, 201)

        login_resp = self.client.post('/auth/login', json={
            'email': 'admin2@example.com',
            'password': 'secret123'
        })
        self.assertEqual(login_resp.status_code, 200)
        token = login_resp.get_json()['access_token']

        upload_resp = self.client.post('/documents/upload', data={
            'title': 'Incident Guide',
            'file': (io.BytesIO(b'When an incident occurs, escalate immediately and follow the escalation checklist.'), 'incident.txt')
        }, headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(upload_resp.status_code, 201)
        document_id = upload_resp.get_json()['id']

        question_resp = self.client.post('/questions/', json={
            'document_id': document_id,
            'question': 'How should I respond when an incident occurs?'
        }, headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(question_resp.status_code, 200)
        self.assertIn('answer', question_resp.get_json())


if __name__ == '__main__':
    unittest.main()
