import os
import json
import requests as req
from datetime import datetime, tzinfo
from datetime import timedelta
from datetime import timezone
import pymongo
import logging
from dotenv import load_dotenv
load_dotenv()

client = pymongo.MongoClient(os.environ['MONGO_URI'])
mongo_collection_token = client['coral']['toke']

def main():
    tokeninfo = mongo_collection_token.find_one({})

    expiration_message = check_refresh_token_expires(tokeninfo)
    mongo_collection_token.update_one({}, {"$set": {'expiration_message': expiration_message }})

    if is_access_token_expired(tokeninfo):
        logging.info("Access token expired") # TODO save to object 
        refresh_json_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'refresh_token_resp.json')
        token_data = read_json_file(refresh_json_path)
        new_token_data = refresh_access_token(token_data['data']['refresh_token'], os.environ['CLIENT_ID'])
        
        access_token_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "access_token.txt")
        token_file = open(access_token_file_path, "w")
        token_file.write(new_token_data['access_token'])
        token_file.close()

        access_exp_dt = calc_access_expiration(new_token_data['date'], new_token_data['expires_in'])
        mongo_collection_token.update_one({}, {"$set": {'until': access_exp_dt }})


def read_json_file(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    return data

def parse_date_response(date_response):
    return datetime.strptime(date_response, "%a, %d %b %Y %H:%M:%S %Z")

def check_refresh_token_expires(tokeninfo):
    # shorten the actual expiration by 10 days to get notified ahead of time
    adjusted_expire = tokeninfo['refresh_until'] - (60*60*24*10)
    date_about_to_expire = tokeninfo['refresh_origin'] + timedelta(seconds=adjusted_expire)
    date_about_to_expire = date_about_to_expire.replace(tzinfo=timezone.utc)
    if date_about_to_expire < datetime.now(tz=timezone.utc):
        timedelta_from_expiration = tokeninfo['refresh_origin'] + timedelta(seconds=tokeninfo['refresh_until']) - datetime.now()
        expiration_message = "Refresh token about to expire in {} hours".format(timedelta_from_expiration / 60 / 60)
        print(expiration_message)
        return expiration_message
    else:
        return None

def is_access_token_expired(tokeninfo):
    return tokeninfo['until'].replace(tzinfo=timezone.utc) < datetime.now(tz=timezone.utc)

def calc_access_expiration(date, expires_in):  
    # subtract 3 minutes to account for scheduled frequency of this script
    return parse_date_response(date) + timedelta(seconds=expires_in - 182) 

def refresh_access_token(refresh_token, client_id):
    payload = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": client_id
    }
    r = req.post("https://api.tdameritrade.com/v1/oauth2/token", data=payload)
    headers = dict(r.headers)
    resp = r.json()
    return {
        "date": headers['Date'],
        "access_token": resp['access_token'],
        "expires_in": resp['expires_in']
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
