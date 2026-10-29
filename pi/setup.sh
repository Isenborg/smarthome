#!/bin/sh
# Installs/updates the dashboard on the Pi. Safe to run repeatedly (deploy.sh runs it).
set -eu
cd "$(dirname "$0")/.."

# Emoji font for the weather icons
if ! dpkg -s fonts-noto-color-emoji >/dev/null 2>&1; then
  sudo apt-get install -y fonts-noto-color-emoji
fi

# Never blank the screen
sudo raspi-config nonint do_blanking 1

# Python environment
[ -d .venv ] || python3 -m venv .venv
.venv/bin/pip install --quiet --disable-pip-version-check -r requirements.txt

[ -f config.toml ] || cp config.example.toml config.toml

# Server: systemd user service, started at boot
mkdir -p ~/.config/systemd/user
cp pi/smarthome.service ~/.config/systemd/user/
sudo loginctl enable-linger "$USER"
systemctl --user daemon-reload
systemctl --user enable smarthome.service
systemctl --user restart smarthome.service

# Kiosk browser: started by the desktop at login
chmod +x pi/kiosk.sh
mkdir -p ~/.config/autostart
cp pi/kiosk.desktop ~/.config/autostart/smarthome-kiosk.desktop

echo "setup done"
