import os
from user_oauth import UserOAuthService

'''
TDA prereq is to get a new refresh token which expires in 90 days.
The response also comes with an access token which expires in 30 minutes.
The refresh token is used to get a new access tokens.
'''
if __name__ == "__main__":
    if (not 'CLIENT_ID' in os.environ) or (not 'TDA_OUTPUT_PATH'):
        print('Environment vars CLIENT_ID and TDA_OUTPUT_PATH required.')
        exit()
    UserOAuthService(client_id=os.environ['CLIENT_ID']).auth(output=os.environ['TDA_REFRESH_PATH'])
