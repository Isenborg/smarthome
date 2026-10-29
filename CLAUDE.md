# smarthome

A living-room "smart frame": an old monitor + Raspberry Pi showing our schedules,
weather, etc., controllable via a Telegram bot (and later Google Home).

## The Pi

- Raspberry Pi 3 Model B Rev 1.2 — 4 cores, 1 GB RAM, 15 GB SD card
- Raspberry Pi OS 12 (bookworm), **32-bit** (armv7l), labwc (Wayland) desktop
- Autologin as `pi`; monitor on HDMI at 1920x1080
- Wired ethernet at `192.168.0.114` (`raspberrypi.local`)
- Installed: Chromium, Firefox, Python 3.11, git. No Node, no Docker.
- Power supply is too weak (`vcgencmd get_throttled` reports under-voltage);
  runs hot (~78 °C) under load. Keep the frontend lightweight.

## Access

```sh
ssh pi@192.168.0.114        # key: ~/.ssh/id_rsa (passphrase in macOS keychain)
```

Passwordless `sudo` works. To act on the screen over SSH:

```sh
export XDG_RUNTIME_DIR=/run/user/1000 WAYLAND_DISPLAY=wayland-0
grim -s 0.5 /tmp/screen.png   # screenshot
```

## Deploying

`./deploy.sh` rsyncs to `~/smarthome` on the Pi (never touching its `config.toml`
or `.venv`) and runs `pi/setup.sh`. The server runs as the systemd user service
`smarthome` (linger enabled, so it starts at boot); Chromium kiosk is started by
`~/.config/autostart/smarthome-kiosk.desktop`. The Mac's default `python3` is
3.10 — use `/opt/homebrew/bin/python3.11` for local runs (needs `tomllib`).

## Gotchas found so far

- Chromium kiosk flags that are needed: `--ozone-platform=wayland --kiosk
  --password-store=basic` (otherwise a keyring password prompt blocks the screen),
  `--autoplay-policy=no-user-gesture-required`, `--deny-permission-prompts`,
  `--disable-features=WebRtcPipeWireCamera` (otherwise a camera prompt appears).
- YouTube embeds opened directly give "Error 153"; they must be inside a page
  served over http (e.g. localhost) so a referrer is sent.
- Default audio sink is the 3.5 mm jack; HDMI is
  `alsa_output.platform-3f902000.hdmi.hdmi-stereo`. `wpctl set-default`
  segfaults on this version — use `pactl set-default-sink` instead.
- Don't `pkill -f` a pattern that also appears in your own ssh command line.
