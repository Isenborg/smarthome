#!/bin/sh
# Copies the project to the Pi and runs the setup there. Run from your Mac.
# The screen reloads by itself when the web files change.
set -eu
cd "$(dirname "$0")"
PI=${PI:-pi@192.168.0.114}

rsync -az --delete \
  --exclude .git --exclude .venv --exclude __pycache__ --exclude config.toml --exclude .DS_Store \
  ./ "$PI:smarthome/"

ssh "$PI" 'sh smarthome/pi/setup.sh'
