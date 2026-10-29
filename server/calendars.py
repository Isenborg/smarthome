"""Calendars from private iCal (ICS) links: iCloud, Google, Outlook."""

from datetime import date, datetime, timedelta
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

import icalendar
import recurring_ical_events


def _download(url):
    if url.startswith("webcal://"):
        url = "https://" + url[len("webcal://"):]
    req = Request(url, headers={"User-Agent": "smarthome/1.0"})
    with urlopen(req, timeout=30) as resp:
        return resp.read()


def _events(cal_cfg, start, end, tz):
    cal = icalendar.Calendar.from_ical(_download(cal_cfg["url"]))
    for ev in recurring_ical_events.of(cal).between(start, end):
        if str(ev.get("STATUS", "")).upper() == "CANCELLED":
            continue
        s = ev["DTSTART"].dt
        e = ev["DTEND"].dt if ev.get("DTEND") else None
        if not isinstance(s, datetime):  # all-day
            yield {
                "all_day": True,
                "start": s,
                "end": e if isinstance(e, date) and e > s else s + timedelta(days=1),
                "title": str(ev.get("SUMMARY", "(no title)")),
            }
            continue
        s = s.replace(tzinfo=tz) if s.tzinfo is None else s.astimezone(tz)
        if isinstance(e, datetime):
            e = e.replace(tzinfo=tz) if e.tzinfo is None else e.astimezone(tz)
        else:
            e = s
        yield {
            "all_day": False,
            "start": s,
            "end": e,
            "title": str(ev.get("SUMMARY", "(no title)")),
            "location": str(ev.get("LOCATION", "")),
        }


def build_agenda(calendars, timezone, days):
    """Events for today + the next `days - 1` days, grouped per day."""
    tz = ZoneInfo(timezone)
    today = datetime.now(tz).date()
    start = datetime.combine(today, datetime.min.time(), tz)
    end = start + timedelta(days=days)

    buckets = {today + timedelta(days=i): [] for i in range(days)}
    errors = []
    for cal_cfg in calendars:
        tag = {"person": cal_cfg["person"], "color": cal_cfg.get("color", "#888888")}
        try:
            for ev in _events(cal_cfg, start, end, tz):
                if ev["all_day"]:
                    d = max(ev["start"], today)
                    while d < ev["end"] and d in buckets:
                        buckets[d].append({**tag, "all_day": True, "title": ev["title"], "sort": ""})
                        d += timedelta(days=1)
                else:
                    d = ev["start"].date()
                    if d < today and ev["end"] > start:
                        d = today  # started earlier, still ongoing
                    if d in buckets:
                        buckets[d].append({
                            **tag,
                            "all_day": False,
                            "title": ev["title"],
                            "location": ev["location"],
                            "start": ev["start"].strftime("%H:%M"),
                            "end": ev["end"].strftime("%H:%M"),
                            "end_iso": ev["end"].isoformat(),
                            "sort": ev["start"].isoformat(),
                        })
        except Exception as exc:
            errors.append(f"{cal_cfg.get('name', cal_cfg['person'])}: {exc}")

    out = []
    for d, events in buckets.items():
        events.sort(key=lambda e: (e["sort"], e["person"]))
        for e in events:
            del e["sort"]
        out.append({"date": d.isoformat(), "events": events})
    return {"days": out, "errors": errors}
