#!/bin/bash

source .env
scp tda-auth/refresh_token_resp.json "$SSH_HOST":tda-auth/
