# smarthome

A living-room dashboard on an old monitor + Raspberry Pi 3: clock, weather for
Linköping, and our calendars (iCloud, Outlook, Google) side by side.

## How it works

- `server/` — small Python server (stdlib + `icalendar`). Fetches weather from
  [Open-Meteo](https://open-meteo.com) every 15 min and the calendars every 10 min,
  and serves the page plus `/api/state`.
- `web/` — the dashboard page (plain HTML/CSS/JS), shown full-screen by Chromium.
  It reloads itself when its files change.
- `pi/` — systemd user service for the server, kiosk launcher, setup script.

## Deploy

From the Mac:

```sh
./deploy.sh
```

This copies the project to `~/smarthome` on the Pi and runs `pi/setup.sh` there.

## Adding calendars

Calendar links are secret, so they only live in `~/smarthome/config.toml` on the Pi
(git-ignored). See `config.example.toml` for where to find each link. After editing:

```sh
ssh pi@192.168.0.114 'systemctl --user restart smarthome'
```

## Run locally

Needs Python 3.11+.

```sh
python3.11 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp config.example.toml config.toml
.venv/bin/python -m server.app     # http://localhost:8000
```
