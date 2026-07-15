import os
import unittest

from config import get_admin_secret, get_database_uri, get_jwt_secret_key


class ConfigTest(unittest.TestCase):
    def test_environment_values_are_used(self):
        os.environ['JWT_SECRET_KEY'] = 'test-jwt-secret'
        os.environ['ADMIN_SECRET'] = 'test-admin-secret'

        self.assertEqual(get_jwt_secret_key(), 'test-jwt-secret')
        self.assertEqual(get_admin_secret(), 'test-admin-secret')
        self.assertTrue(get_database_uri().startswith('sqlite:///') or get_database_uri().startswith('postgresql://'))


if __name__ == '__main__':
    unittest.main()
