import os
import logging
from auth_tokens import read_json_file, AuthService

def main():
    refresh_json_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'refresh_token_resp.json')
    token_data = read_json_file(refresh_json_path)
    AuthService(refresh_token_payload=token_data, client_id=os.environ['CLIENT_ID'])

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
