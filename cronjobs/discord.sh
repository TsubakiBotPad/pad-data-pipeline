#!/bin/bash

set -e
set -x

WEBHOOK_BASE_URL="https://discordapp.com/api/webhooks"
declare -rx PRIVATE_WEBHOOK_URL="$WEBHOOK_BASE_URL/000000000000000000/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
declare -rx PUBLIC_WEBHOOK_URL="$WEBHOOK_BASE_URL/000000000000000000/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

function hook_alert {
    echo "$1"
    data="{\"username\": \"pipeline\", \"content\": \"$1\"}"
    curl -H "Content-Type: application/json" \
        -X POST \
        -d "$data" $PRIVATE_WEBHOOK_URL
}

function hook_file {
  curl -F "data=@$1" $PRIVATE_WEBHOOK_URL
}

function public_hook_file {
  curl -F "data=@$1" $PUBLIC_WEBHOOK_URL
}
