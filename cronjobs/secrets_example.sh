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
