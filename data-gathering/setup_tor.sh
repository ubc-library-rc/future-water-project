#!/bin/bash

tor_password="scholarly_password"
hashed_password=$(tor --hash-password $tor_password)
echo "ControlPort 9051" | tee /etc/tor/torrc
echo "HashedControlPassword $hashed_password" | tee -a /etc/tor/torrc