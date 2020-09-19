#!/bin/bash

set -e
set -x

WEBHOOK_BASE_URL="https://discordapp.com/api/webhooks"
declare -rx PRIVATE_WEBHOOK_URL="$WEBHOOK_BASE_URL/756665273251266671/h6rCZyftIPOr94Bq-IR8evVoZNqc6urBOmxTveAUhzcDWQdYIrlnNUPMG77l490X2JVm"
declare -rx PUBLIC_WEBHOOK_URL="$WEBHOOK_BASE_URL/756665273251266671/h6rCZyftIPOr94Bq-IR8evVoZNqc6urBOmxTveAUhzcDWQdYIrlnNUPMG77l490X2JVm"

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
