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
            'email': 'admin@example.com',
            'password': 'secret123',
            'admin_secret': 'admin-secret-key-change-me'
        })
        self.assertEqual(signup_resp.status_code, 201)

        login_resp = self.client.post('/auth/login', json={
            'email': 'admin@example.com',
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
        sop_id = create_resp.get_json()['id']

        list_resp = self.client.get('/sops/', headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(list_resp.status_code, 200)
        self.assertEqual(len(list_resp.get_json()), 1)

        question_resp = self.client.post('/questions/', json={
            'sop_id': sop_id,
            'question': 'How should I handle an incident?'
        }, headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(question_resp.status_code, 200)
        question_payload = question_resp.get_json()
        self.assertIn('answer', question_payload)
        self.assertIn('sources', question_payload)
        self.assertTrue(isinstance(question_payload['sources'], list))
        self.assertGreaterEqual(len(question_payload['sources']), 1)

        history_resp = self.client.get('/answers/', headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(history_resp.status_code, 200)
        self.assertEqual(len(history_resp.get_json()), 1)

    def test_user_cannot_delete_another_admin_sop(self):
        self.client.post('/auth/signup', json={
            'email': 'admin1@example.com',
            'password': 'secret123',
            'admin_secret': 'admin-secret-key-change-me'
        })
        self.client.post('/auth/signup', json={
            'email': 'admin2@example.com',
            'password': 'secret123',
            'admin_secret': 'admin-secret-key-change-me'
        })

        admin1_token = self.client.post('/auth/login', json={
            'email': 'admin1@example.com',
            'password': 'secret123'
        }).get_json()['access_token']

        admin2_token = self.client.post('/auth/login', json={
            'email': 'admin2@example.com',
            'password': 'secret123'
        }).get_json()['access_token']

        create_resp = self.client.post('/sops/', json={
            'title': 'Finance SOP',
            'content': 'Approvals require director signoff.',
            'department_name': 'Finance'
        }, headers={'Authorization': f'Bearer {admin1_token}'})
        sop_id = create_resp.get_json()['id']

        delete_resp = self.client.delete(f'/sops/{sop_id}', headers={'Authorization': f'Bearer {admin2_token}'})
        self.assertEqual(delete_resp.status_code, 403)

    def test_answer_history_is_user_scoped_and_clearable(self):
        self.client.post('/auth/signup', json={
            'email': 'admin@example.com',
            'password': 'secret123',
            'admin_secret': 'admin-secret-key-change-me'
        })
        self.client.post('/auth/signup', json={
            'email': 'user@example.com',
            'password': 'secret123'
        })

        admin_token = self.client.post('/auth/login', json={
            'email': 'admin@example.com',
            'password': 'secret123'
        }).get_json()['access_token']

        user_token = self.client.post('/auth/login', json={
            'email': 'user@example.com',
            'password': 'secret123'
        }).get_json()['access_token']

        sop_id = self.client.post('/sops/', json={
            'title': 'IT SOP',
            'content': 'Restart the service, then escalate on repeated failures.',
            'department_name': 'IT'
        }, headers={'Authorization': f'Bearer {admin_token}'}).get_json()['id']

        self.client.post('/questions/', json={
            'sop_id': sop_id,
            'question': 'What do I do when service fails repeatedly?'
        }, headers={'Authorization': f'Bearer {user_token}'})

        user_history = self.client.get('/answers/', headers={'Authorization': f'Bearer {user_token}'})
        admin_history = self.client.get('/answers/', headers={'Authorization': f'Bearer {admin_token}'})

        self.assertEqual(user_history.status_code, 200)
        self.assertEqual(admin_history.status_code, 200)
        self.assertEqual(len(user_history.get_json()), 1)
        self.assertEqual(len(admin_history.get_json()), 0)

        clear_resp = self.client.delete('/answers/', headers={'Authorization': f'Bearer {user_token}'})
        self.assertEqual(clear_resp.status_code, 200)

        cleared_history = self.client.get('/answers/', headers={'Authorization': f'Bearer {user_token}'})
        self.assertEqual(len(cleared_history.get_json()), 0)


if __name__ == '__main__':
    unittest.main()
