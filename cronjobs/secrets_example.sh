#!/bin/bash

set -e
set -x

declare -rx AWS_ACCESS_KEY_ID="GetThisFromAWSCred"
declare -rx AWS_SECRET_ACCESS_KEY="FromAWsConsole"
declare -rx MYSQL_USER="whateverYouMadeYourSqlUserNameToBe"
declare -rx MYSQL_PASSWORD="your sql password"
declare -rx JP_PAD_USER_UUID="00000000-0000-0000-0000-000000000000"
declare -rx JP_PAD_USER_INTID="111111111"
declare -rx JP_PAD_USER_COLOR_GROUP="blue"
declare -rx NA_PAD_USER_UUID="00000000-0000-0000-0000-000000000000"
declare -rx NA_PAD_USER_INTID="111111111"
declare -rx NA_PAD_USER_COLOR_GROUP="red"
declare -rx PRIVATE_ERROR_WEBHOOK_URL="https://discordapp.com/api/webhooks/THIS/IS-YOUR-WEBHOOK-URL"
declare -rx PRIVATE_WARN_WEBHOOK_URL="https://discordapp.com/api/webhooks/THIS/IS-YOUR-WEBHOOK-URL2"
declare -rx PRIVATE_INFO_WEBHOOK_URL="https://discordapp.com/api/webhooks/THIS/IS-YOUR-WEBHOOK-URL3"
declare -rx PUBLIC_WEBHOOK_URL="https://discordapp.com/api/webhooks/THIS/IS-YOUR-WEBHOOK-URL4"
declare -rx NOTIFICATION_DISCORD_ROLE_ID="12398612894698234"
