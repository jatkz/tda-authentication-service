#!/bin/bash

source .env
scp -r ./tda-auth "$SSH_HOST":
