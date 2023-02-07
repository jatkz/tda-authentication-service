import json
import os
import unittest
from reauth import AuthService, read_json_file
import datetime
from dotenv import load_dotenv
from oauth import UserOAuthService


load_dotenv()
load_dotenv(os.environ["DOTENV_PATH"])


class TestOAuthService(unittest.TestCase):
    @unittest.skip("turn off for now")
    def test_oauth(self):
        UserOAuthService(os.environ["CLIENT_ID"]).auth(
            os.environ["TDA_REFRESH_TOKEN_PATH"]
        )


class TestAuthTokens(unittest.TestCase):
    def test_refresh_expired_returns_false(self):
        # join __dir__
        refresh_token_path = os.path.join(
            os.getcwd(), "test/test-data/refresh_expired_returns_false.json"
        )

        AuthService(
            refresh_token_path=refresh_token_path,
            client_id=os.environ["CLIENT_ID"],
            refresh_status_path=os.environ["TDA_REFRESH_STATUS_PATH"],
            access_token_path=os.environ["TDA_ACCESS_TOKEN_PATH"],
        ).handle_refresh_token_status()

        with open(os.environ["TDA_REFRESH_STATUS_PATH"], "r", encoding="utf-8") as f:
            refresh_status_file = f.read()

        self.assertEqual(int(refresh_status_file) > 0, False)
        os.remove(os.environ["TDA_REFRESH_STATUS_PATH"])

    def test_access_token_updates(self):
        AuthService(
            refresh_token_path=os.environ["TDA_REFRESH_TOKEN_PATH"],
            client_id=os.environ["CLIENT_ID"],
            refresh_status_path=os.environ["TDA_REFRESH_STATUS_PATH"],
            access_token_path=os.environ["TDA_ACCESS_TOKEN_PATH"],
        ).handle_access_token()

        access_token_payload = read_json_file(os.environ["TDA_ACCESS_TOKEN_PATH"])

        self.assertIsNotNone(access_token_payload["data"]["access_token"])
        os.remove(os.environ["TDA_ACCESS_TOKEN_PATH"])


if __name__ == "__main__":
    unittest.main()
