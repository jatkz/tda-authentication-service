import os
import json
import requests as req
from datetime import datetime, tzinfo
from datetime import timedelta
from datetime import timezone
import logging
from dotenv import load_dotenv
from pathlib import Path
load_dotenv()

class AuthService:
    def __init__(self, refresh_token_payload, client_id):
        self.refresh_token_payload = refresh_token_payload
        self.client_id = client_id

    def handle(self):
        self.handle_refresh_token()
        self.handle_access_token()

    def handle_refresh_token(self):
        refresh_token_expiration_date = parse_date_response(self.refresh_token_payload['headers']['Date']) + timedelta(seconds=self.refresh_token_payload['data']['refresh_token_expires_in'])
        expiration_in_seconds = (refresh_token_expiration_date - datetime.now()).total_seconds()

        refresh_status_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "refresh_status")
        refresh_status = open(refresh_status_file_path, "w")
        token_file.write(expiration_in_seconds)
        token_file.close()

        if expiration_in_seconds < 0:
            exit(1)


    def handle_access_token(self):
        access_json_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'access_token_resp.json')
        # check expiration based which token payload
        if Path(access_json_path).is_file():
            latest_token_payload = read_json_file(access_json_path)
        else:
            latest_token_payload = refresh_token_payload

        access_token_expiration_date = parse_date_response(latest_token_payload['headers']['Date']) + timedelta(seconds=latest_token_payload['data']['expires_in'])
        expiration_in_seconds = (access_token_expiration_date - datetime.now()).total_seconds()

        # if expiration is in less than 5 minutes
        if expiration_in_seconds < 300:
            new_token_data = fetch_access_token(refresh_token_payload['data']['refresh_token'], self.client_id)
            access_token_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "access_token_resp.json")
            token_file = open(access_token_file_path, "w")
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



if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        dir_path = os.path.dirname(os.path.realpath(__file__))
        log_file_path = os.path.join(dir_path, "error_access_token.log")
        log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        dt_fmt = '%m/%d/%Y %I:%M:%S %p'
        logging.basicConfig(filename=log_file_path, filemode='w', level=logging.INFO, format=log_fmt, datefmt=dt_fmt)
        logging.error(type(e))
        logging.error(e.args)
        logging.error(e)
