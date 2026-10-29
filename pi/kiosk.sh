#!/bin/sh
# Opens the dashboard full-screen once the server is up. Started by the desktop at login.

URL=http://localhost:8000/

for _ in $(seq 60); do
  curl -fs -o /dev/null "$URL" && break
  sleep 1
done

exec chromium \
  --ozone-platform=wayland \
  --kiosk \
  --password-store=basic \
  --noerrdialogs \
  --disable-session-crashed-bubble \
  --no-first-run \
  --check-for-update-interval=31536000 \
  --autoplay-policy=no-user-gesture-required \
  --deny-permission-prompts \
  --disable-features=WebRtcPipeWireCamera,Translate \
  "$URL"
