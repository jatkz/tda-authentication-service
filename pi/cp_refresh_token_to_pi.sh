#!/usr/bin/env bash

source .env
scp $TDA_REFRESH_PATH "$SSH_HOST":tda-auth/
