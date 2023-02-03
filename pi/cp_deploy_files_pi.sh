#!/usr/bin/env bash

source .env
scp -r ./src "$SSH_HOST":tda-auth/
./pi/cp_refresh_token_to_pi.sh
scp -r ./pi/setup.sh "$SSH_HOST":tda-auth/