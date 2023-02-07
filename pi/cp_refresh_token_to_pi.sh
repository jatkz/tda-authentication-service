#!/usr/bin/env bash

source .env
scp $TDA_REFRESH_TOKEN_PATH "$SSH_HOST":tda-auth/
