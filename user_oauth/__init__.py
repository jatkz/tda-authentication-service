from urllib.parse import urlencode, urlparse, parse_qs, unquote
from dotenv import load_dotenv
import os
import requests as req
import json
from datetime import datetime

load_dotenv()

class UserOAuthService():
    def __init__(self, client_id) -> None:
        if client_id == "":
            print("client_id is not set")
            exit(1)

        self.client_id = client_id

        if not "@AMER.OAUTHAP" in client_id:
            self.client_id += "@AMER.OAUTHAP"
    
    def auth(self, output):
        auth_url = generate_secure_signin_url(self.client_id)
        print('\nSecurely login to the tda account')
        print('\nURL => ' + auth_url)
        print('\nAfter login, copy the url')
        redirected_url_with_code = input('\nEnter the full url: ')

        code = getQueryParam(redirected_url_with_code, 'code')
        code_decoded = unquote(code)
        access_token_resp = get_refresh_token(code_decoded, self.client_id)
        
        # validate the token payload is the expected interface
        token_data_validation(access_token_resp)

        # write refresh token to file
        with open(output, 'w') as f:
            f.write(json.dumps(access_token_resp, indent=4))

        print('\nrefresh token saved')

def generate_secure_signin_url(client_id):
    params = {
        "response_type": "code",
        "redirect_uri": "https://google.com",
        "client_id": client_id
    }
    urlencode_values = urlencode(params)
    auth_url = "https://auth.tdameritrade.com/auth?" + urlencode_values
    return auth_url

def getQueryParam(url, param):
    url_parts = urlparse(url)
    query = parse_qs(url_parts.query)
    return query[param][0]

def get_refresh_token(code, client_id, redirect_uri="https://google.com"):
    payload = {
        "grant_type": "authorization_code",
        "access_type": "offline",
        "code": code,  # step 2
        "client_id": client_id,
        "redirect_uri": redirect_uri
    }
    r = req.post("https://api.tdameritrade.com/v1/oauth2/token", data=payload)
    headers = dict(r.headers)
    resp = r.json()
    return {
        "headers": headers,
        "data": resp
    }

def token_data_validation(token_data):
    if not ('data' in token_data and 'headers' in token_data):
        raise Exception("Invalid token data")

    if not ('access_token' in token_data['data'] and 'refresh_token' in token_data['data']):
        raise Exception("Invalid token data")

    if not ('Date' in token_data['headers']):
        raise Exception("Invalid headers date missing")
    
    if not ('refresh_token_expires_in' in token_data['data'] and 'expires_in' in token_data['data']):
        raise Exception("Invalid token expiration data")

    if token_data['data']['refresh_token_expires_in'] != 7776000:
        # Data base that the expire parameter changed
        print("Refresh token expire parameter changed")
        raise Exception("Refresh token expiration had a system change")

    if token_data['data']['expires_in'] != 1800:
        print("Access token expire parameter changed")
        raise Exception("Access token expiration had a system change")

    return
