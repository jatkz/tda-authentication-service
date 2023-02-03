import os
import json
import requests as req
from datetime import datetime
from datetime import timedelta
from pathlib import Path

class AuthService:
    def __init__(self, 
        refresh_token_payload, 
        client_id,
        refresh_status_path,
        access_token_path
        ):
        self.refresh_token_payload = refresh_token_payload
        self.client_id = client_id
        self.refresh_status_path = refresh_status_path
        self.access_token_path = access_token_path

    def handle(self):
        if self.handle_refresh_token_status():
            return
        self.handle_access_token()

    def handle_refresh_token_status(self):
        refresh_token_expiration_date = parse_date_response(self.refresh_token_payload['headers']['Date']) + timedelta(seconds=self.refresh_token_payload['data']['refresh_token_expires_in'])
        expiration_in_seconds = (refresh_token_expiration_date - datetime.now()).total_seconds()

        refresh_status_file = open(self.refresh_status_path, "w")
        refresh_status_file.write(expiration_in_seconds)
        refresh_status_file.close()

        return expiration_in_seconds > 0


    def handle_access_token(self):
        # check expiration based which token payload
        if Path(self.access_token_path).is_file():
            latest_token_payload = read_json_file(self.access_token_path)
        else:
            latest_token_payload = self.refresh_token_payload

        # check expiration
        access_token_expiration_date = parse_date_response(latest_token_payload['headers']['Date']) + timedelta(seconds=latest_token_payload['data']['expires_in'])
        expiration_in_seconds = (access_token_expiration_date - datetime.now()).total_seconds()

        # if expiration
        if expiration_in_seconds < 300:
            new_token_data = fetch_access_token(latest_token_payload['data']['refresh_token'], self.client_id)
            token_file = open(self.access_token_file_path, "w")
            token_file.write(new_token_data)
            token_file.close()


def main():
    refresh_json_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'refresh_token_resp.json')
    token_data = read_json_file(refresh_json_path)
    AuthService(refresh_token_payload=token_data, client_id=os.environ['CLIENT_ID'])


def read_json_file(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    return data

def parse_date_response(date_response):
    return datetime.strptime(date_response, "%a, %d %b %Y %H:%M:%S %Z")

def fetch_access_token(refresh_token, client_id):
    payload = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": client_id
    }
    r = req.post("https://api.tdameritrade.com/v1/oauth2/token", data=payload)
    headers = dict(r.headers)
    resp = r.json()
    return {
        "headers": headers,
        "data": resp
    }
