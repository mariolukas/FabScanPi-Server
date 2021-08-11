#!/bin/sh
mkdir $HOME/secrets
# Decrypt the file
# --batch to prevent interactive command
# --yes to assume "yes" for questions
gpg --quiet --batch --yes --decrypt --passphrase="$FABSCAN_KEY_PASSPHRASE" \
--output $HOME/secrets/fabscan.key fabscan.key.gpg