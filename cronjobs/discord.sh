#!/bin/bash

set -e
set -x

WEBHOOK_BASE_URL="https://discordapp.com/api/webhooks"
declare -rx PRIVATE_WEBHOOK_URL="$WEBHOOK_BASE_URL/744624214002237440/v4GZIInJ8t24Mm_HaI3csRma19DNLbt2kTc3Biq0-yaWf6W6bCDWAPLFKhnK5U8SFHV-"
declare -rx PUBLIC_WEBHOOK_URL="$WEBHOOK_BASE_URL/744624214002237440/v4GZIInJ8t24Mm_HaI3csRma19DNLbt2kTc3Biq0-yaWf6W6bCDWAPLFKhnK5U8SFHV-"

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
