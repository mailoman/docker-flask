#!/usr/bin/env bash

echo "Please enter valid credentials for auth"
echo "login(email):"
read email

echo "password:"
read -s password

cmd="-X POST -s -H \"Accept: application/json\" -H \"Content-type: application/json\" -d '{\"email\": \"${email}\", \"password\": \"${password}\"}' http://127.0.0.1:5000/login"

res=`echo "${cmd}"|xargs curl`
token=`echo $res | grep -oE "\"authentication_token\": \"([^\"]+)" | cut -d '"' -f4`
echo $token

