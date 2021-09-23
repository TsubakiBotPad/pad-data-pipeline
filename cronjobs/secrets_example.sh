#!/usr/bin/env bash

set -e
set -x

declare -x AWS_ACCESS_KEY_ID="GetThisFromAWSCred"
declare -x AWS_SECRET_ACCESS_KEY="FromAWsConsole"
declare -x MYSQL_USER="whateverYouMadeYourSqlUserNameToBe"
declare -x MYSQL_PASSWORD="your sql password"
declare -x JP_PAD_USER_UUID="00000000-0000-0000-0000-000000000000"
declare -x JP_PAD_USER_INTID="111111111"
declare -x JP_PAD_USER_COLOR_GROUP="blue"
declare -x NA_PAD_USER_UUID="00000000-0000-0000-0000-000000000000"
declare -x NA_PAD_USER_INTID="111111111"
declare -x NA_PAD_USER_COLOR_GROUP="red"
declare -x PRIVATE_ERROR_WEBHOOK_URL="https://discordapp.com/api/webhooks/THIS/IS-YOUR-WEBHOOK-URL"
declare -x PRIVATE_WARN_WEBHOOK_URL="https://discordapp.com/api/webhooks/THIS/IS-YOUR-WEBHOOK-URL2"
declare -x PRIVATE_INFO_WEBHOOK_URL="https://discordapp.com/api/webhooks/THIS/IS-YOUR-WEBHOOK-URL3"
declare -x PUBLIC_WEBHOOK_URL="https://discordapp.com/api/webhooks/THIS/IS-YOUR-WEBHOOK-URL4"
declare -x NOTIFICATION_DISCORD_ROLE_ID="12398612894698234"
