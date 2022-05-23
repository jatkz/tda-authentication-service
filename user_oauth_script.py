from urllib.parse import urlencode, urlparse, parse_qs, unquote
from dotenv import load_dotenv
import os
import requests as req
import json
import datetime
import pymongo

load_dotenv()

def main(client_id):
    if client_id == "":
        print("client_id is not set")
        exit(1)

    auth_url = generate_secure_signin_url(client_id)
    print('\nSecurely login to the tda account')
    print('\nURL => ' + auth_url)
    print('\nAfter login, copy the url')
    redirected_url_with_code = input('\nEnter the full url: ')

    code = getQueryParam(redirected_url_with_code, 'code')
    code_decoded = unquote(code)
    access_token_resp = get_refresh_token(code_decoded, client_id)
    token_data_validation(access_token_resp)
    refresh_date = parse_date_response(access_token_resp['headers']['Date'])
    client = pymongo.MongoClient(os.environ['MONGO_URI'])
    mongo_collection_token = client['coral']['toke']
    mongo_collection_token.update_one({}, {"$set": {'refresh_origin': refresh_date, 'refresh_until': access_token_resp['data']['refresh_token_expires_in'] }})
    dict_to_jsonfile(access_token_resp, 'tda-auth/refresh_token_resp.json')
    print('\nrefresh_token_resp.json saved and databased as well')


def parse_date_response(date_response):
    return datetime.strptime(date_response, "%a, %d %b %Y %H:%M:%S %Z")

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

def dict_to_jsonfile(data_dict, filename):
    with open(filename, 'w') as f:
        f.write(json.dumps(data_dict, indent=4))

'''
TDA prereq is to get a new refresh token which expires in 90 days.
The response also comes with an access token which expires in 30 minutes.
The refresh token is used to get a new access tokens.
'''
if __name__ == "__main__":
    main(os.environ['CLIENT_ID'])