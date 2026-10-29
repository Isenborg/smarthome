"""Dashboard server: refreshes data in the background and serves web/ + /api/state.

Run with:  python -m server.app
"""

import json
import logging
import os
import threading
import time
import tomllib
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from . import calendars, weather

ROOT = Path(__file__).resolve().parent.parent
WEB = ROOT / "web"
CONFIG = Path(os.environ.get("SMARTHOME_CONFIG", ROOT / "config.toml"))

log = logging.getLogger("smarthome")
state = {"weather": None, "agenda": None, "errors": {}}
lock = threading.Lock()


def refresher(name, interval, fn):
    def loop():
        while True:
            try:
                value = fn()
                with lock:
                    state[name] = value
                    state["errors"].pop(name, None)
            except Exception as exc:
                log.exception("refreshing %s failed", name)
                with lock:
                    state["errors"][name] = str(exc)
            time.sleep(interval)

    threading.Thread(target=loop, daemon=True, name=name).start()


def web_version():
    # Changes whenever a web file changes, so the page can reload itself after a deploy.
    return str(max(p.stat().st_mtime_ns for p in WEB.rglob("*") if p.is_file()))


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB), **kwargs)

    def do_GET(self):
        if self.path == "/api/state":
            with lock:
                body = json.dumps({**state, "version": web_version()}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            super().do_GET()

    def end_headers(self):
        if self.path != "/api/state":
            self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    def log_message(self, fmt, *args):
        pass


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    cfg = tomllib.loads(CONFIG.read_text())
    loc = cfg["location"]
    server_cfg = cfg.get("server", {})
    days = cfg.get("display", {}).get("days_ahead", 7)

    refresher("weather", 15 * 60, lambda: weather.fetch(loc))
    refresher("agenda", 10 * 60,
              lambda: calendars.build_agenda(cfg.get("calendars", []), loc["timezone"], days))

    host, port = server_cfg.get("host", "127.0.0.1"), server_cfg.get("port", 8000)
    log.info("serving on http://%s:%s", host, port)
    ThreadingHTTPServer((host, port), Handler).serve_forever()


if __name__ == "__main__":
    main()
