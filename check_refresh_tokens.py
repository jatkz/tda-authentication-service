import os
import logging
from reauth import read_json_file, AuthService
from dotenv import load_dotenv

load_dotenv()
load_dotenv(os.environ["DOTENV_PATH"])


def main():
    refresh_json_path = os.environ["TDA_REFRESH_TOKEN_PATH"]
    token_data = read_json_file(refresh_json_path)
    AuthService(
        refresh_token_path=os.environ["TDA_REFRESH_TOKEN_PATH"],
        client_id=os.environ["CLIENT_ID"],
        refresh_status_path=os.environ["TDA_REFRESH_STATUS_PATH"],
        access_token_path=os.environ["TDA_ACCESS_TOKEN_PATH"],
    ).handle()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        dir_path = os.path.dirname(os.path.realpath(__file__))
        log_file_path = os.path.join(dir_path, "error_access_token.log")
        log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        dt_fmt = "%m/%d/%Y %I:%M:%S %p"
        logging.basicConfig(
            filename=log_file_path,
            filemode="w",
            level=logging.INFO,
            format=log_fmt,
            datefmt=dt_fmt,
        )
        logging.error(type(e))
        logging.error(e.args)
        logging.error(e)
