import os
import unittest
from user_oauth import UserOAuthService

class TestOAuthService(unittest.TestCase):

    def test_oauth(self):
        UserOAuthService(os.environ['CLIENT_ID']).auth(os.environ['TDA_OUTPUT_PATH'])

if __name__ == '__main__':
    unittest.main()