import json
import os
from pathlib import Path
import unittest
from auth_tokens import AuthService
import datetime
from dotenv import load_dotenv

load_dotenv()

class TestAuthTokens(unittest.TestCase):

    def test_refresh_success_returns_true(self):
        # generated from user oauth
        refresh_token_payload = {
            'headers': {
                'Date': datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S %Z")
            },
            'data': {
                'refresh_token_expires_in': 777600
            }
        }
        status = AuthService(
            os.environ['CLIENT_ID'],
            refresh_token_payload,
            refresh_status_path=os.environ['TDA_REFRESH_STATUS_PATH'],
            access_token_path=os.environ['TDA_ACCESS_TOKEN_PATH']
            ).handle_refresh_token_status()
        self.assertEqual(status, True)
        
        refresh_status_file = open(os.environ['TDA_REFRESH_STATUS_PATH'], "r").read()
        self.assertEqual(refresh_status_file > 0, True)
        os.remove(os.environ['TDA_REFRESH_STATUS_PATH'])

    def test_refresh_expired_returns_false(self):
        # generated from user oauth
        refresh_token_payload = {
            'headers': {
                'Date': 'Wed Jan 25 2017 16:00:00 GMT'
            },
            'data': {
                'refresh_token_expires_in': 777600
            }
        }
        status = AuthService(
            os.environ['CLIENT_ID'],
            refresh_token_payload,
            refresh_status_path=os.environ['TDA_REFRESH_STATUS_PATH'],
            access_token_path=os.environ['TDA_ACCESS_TOKEN_PATH']
            ).handle_refresh_token_status()
        self.assertEqual(status, False)
        
        refresh_status_file = open(os.environ['TDA_REFRESH_STATUS_PATH'], "r").read()
        self.assertEqual(refresh_status_file > 0, False)
        os.remove(os.environ['TDA_REFRESH_STATUS_PATH'])

    def test_access_token_updates(self):
        # generated real from user oauth
        refresh_token_payload = json.load(open(os.environ['TDA_REFRESH_PATH'], 'r'))
        AuthService(
            os.environ['CLIENT_ID'],
            refresh_token_payload,
            refresh_status_path=os.environ['TDA_REFRESH_STATUS_PATH'],
            access_token_path=os.environ['TDA_ACCESS_TOKEN_PATH']
        ).handle_refresh_token()

        access_token_payload = json.load(open(os.environ['TDA_ACCESS_TOKEN_PATH'], "r"))
        self.assertIs(access_token_payload['data']['refresh_token'])
        os.remove(os.environ['TDA_ACCESS_TOKEN_PATH'])

    def test_access_token_passes_no_updates(self):
        # get real token in order to test this
                # generated from user oauth
        refresh_token_payload = {
            'headers': {
                'Date': 'Wed Jan 25 2017 16:00:00 GMT'
            },
            'data': {
                'expires_in': 1800
            }
        }
        AuthService(
            os.environ['CLIENT_ID'],
            refresh_token_payload,
            refresh_status_path=os.environ['TDA_REFRESH_STATUS_PATH'],
            access_token_path=os.environ['TDA_ACCESS_TOKEN_PATH']
        ).handle_refresh_token()

        self.assertEqual(Path(os.environ['TDA_ACCESS_TOKEN_PATH']).is_file(), False)
        os.remove(os.environ['TDA_ACCESS_TOKEN_PATH'])



if __name__ == '__main__':
    unittest.main()