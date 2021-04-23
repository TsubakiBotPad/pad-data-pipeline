#!/bin/bash

set -e
set -x

cd "$(dirname "$0")" || exit
source ./secrets.sh

function hook_error() {
  echo "$1"
  data="{\"content\": \"$1\"}"
  curl -H "Content-Type: application/json" \
    -X POST \
    -d "$data" $PRIVATE_ERROR_WEBHOOK_URL
}

function hook_warn() {
  echo "$1"
  data="{\"content\": \"$1\"}"
  curl -H "Content-Type: application/json" \
    -X POST \
    -d "$data" $PRIVATE_WARN_WEBHOOK_URL
}

function hook_info() {
  echo "$1"
  data="{\"content\": \"$1\"}"
  curl -H "Content-Type: application/json" \
    -X POST \
    -d "$data" $PRIVATE_INFO_WEBHOOK_URL
}

function hook_file() {
  curl -F "data=@$1" $PRIVATE_INFO_WEBHOOK_URL
}

function public_hook_file() {
  curl -F "data=@$1" $PUBLIC_WEBHOOK_URL
}
