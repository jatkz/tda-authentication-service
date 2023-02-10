# tda-authentication-service

Set up in order to automate getting your personal credentials for the td-ameritrade api access. Contains scripts for deploying to a raspberry-pi server. This will only expose the temporary access token to the machine the script is hosted on.

# Setting up

In order to install dependencies you will need pipenv installed:
`pip install pipenv`

After successful installation:
`pipenv install`

Then activate the shell whenever you would like to use:
`pipenv shell`


### Uploading to PI Server

Here is below code to copy all files needed to run this on a raspberry pi 
```
# source your .env
# Host name should follow {user}@{ipaddress}:{path}
scp -r ./reauth ./check_refresh_tokens.py "$SSH_HOST"
scp "$TDA_REFRESH_TOKEN_PATH" "$SSH_HOST"
```

SSH into PI and run following commands to install dependencies and contab scheduling:
```
pip install requests;
pip install datetime;

sudo nano /etc/crontab;
```

Inside the crontab enter cron expression following this pattern:
```
*/20 8-22 * * 1-5 <user> python ~/home/<user>/check_refresh_tokens.py > /home/<user>/cron.log 2>&1
```

The following ENV variables are required and you can add them to /etc/profile
```
export CLIENT_ID=<APIKEY@AMER.OAUTHAP>
export TDA_REFRESH_TOKEN_PATH="/home/../refresj_token.json"
export TDA_REFRESH_STATUS_PATH="/home/../refresh_status"
export TDA_ACCESS_TOKEN_PATH="/home/../access_token.json"
```

Then follow up with 
```
sudo reboot
```
