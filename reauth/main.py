import json
import requests as req
from datetime import datetime
from datetime import timedelta
from pathlib import Path


class AuthService:
    def __init__(
        self, refresh_token_path, client_id, refresh_status_path, access_token_path
    ):
        refresh_payload = read_json_file(refresh_token_path)
        self.refresh_date = refresh_payload["headers"]["Date"]
        self.refresh_expires_in = refresh_payload["data"]["refresh_token_expires_in"]
        self.refresh_token = refresh_payload["data"]["refresh_token"]
        self.access_token_path = access_token_path
        self.client_id = client_id
        self.refresh_status_path = refresh_status_path

    def handle(self):
        self.handle_refresh_token_status()
        self.handle_access_token()

    def handle_refresh_token_status(self):
        expiration_in_seconds = self.get_expiration_in_seconds()

        # updates file
        with open(self.refresh_status_path, "w", encoding="utf-8") as f:
            f.write(str(expiration_in_seconds))

    def handle_access_token(self):
        new_token_data = fetch_access_token(self.refresh_token, self.client_id)
        with open(self.access_token_path, "w", encoding="utf-8") as f:
            f.write(json.dumps(new_token_data, indent=4))

    def get_expiration_in_seconds(self):
        date_creation = parse_date_response(self.refresh_date)
        expires_in = timedelta(seconds=self.refresh_expires_in)
        refresh_token_expiration_date = date_creation + expires_in
        expiration_in_seconds = (
            refresh_token_expiration_date - datetime.now()
        ).total_seconds()
        # ternary operator to check if expiration_in_seconds is less than 0
        # if it is, then set it to 0
        expiration_in_seconds = (
            0 if expiration_in_seconds < 0 else expiration_in_seconds
        )
        return expiration_in_seconds


def read_json_file(filename):
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def parse_date_response(date_response):
    return datetime.strptime(date_response, "%a, %d %b %Y %H:%M:%S %Z")


def fetch_access_token(refresh_token, client_id):
    payload = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": client_id,
    }
    r = req.post("https://api.tdameritrade.com/v1/oauth2/token", data=payload)
    headers = dict(r.headers)
    resp = r.json()
    return {"headers": headers, "data": resp}
