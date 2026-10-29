// Dashboard: the clock ticks locally, everything else comes from /api/state.

const LOCALE = "en-GB";
let version = null;

// WMO weather codes -> [label, day icon, night icon]
const WEATHER = {
  0: ["Clear", "☀️", "🌙"],
  1: ["Mainly clear", "🌤️", "🌙"],
  2: ["Partly cloudy", "⛅", "☁️"],
  3: ["Overcast", "☁️", "☁️"],
  45: ["Fog", "🌫️", "🌫️"], 48: ["Fog", "🌫️", "🌫️"],
  51: ["Light drizzle", "🌦️", "🌧️"], 53: ["Drizzle", "🌦️", "🌧️"], 55: ["Heavy drizzle", "🌧️", "🌧️"],
  56: ["Freezing drizzle", "🌧️", "🌧️"], 57: ["Freezing drizzle", "🌧️", "🌧️"],
  61: ["Light rain", "🌦️", "🌧️"], 63: ["Rain", "🌧️", "🌧️"], 65: ["Heavy rain", "🌧️", "🌧️"],
  66: ["Freezing rain", "🌧️", "🌧️"], 67: ["Freezing rain", "🌧️", "🌧️"],
  71: ["Light snow", "🌨️", "🌨️"], 73: ["Snow", "🌨️", "🌨️"], 75: ["Heavy snow", "❄️", "❄️"],
  77: ["Snow grains", "🌨️", "🌨️"],
  80: ["Showers", "🌦️", "🌧️"], 81: ["Showers", "🌧️", "🌧️"], 82: ["Heavy showers", "🌧️", "🌧️"],
  85: ["Snow showers", "🌨️", "🌨️"], 86: ["Snow showers", "🌨️", "🌨️"],
  95: ["Thunderstorm", "⛈️", "⛈️"], 96: ["Thunderstorm", "⛈️", "⛈️"], 99: ["Thunderstorm", "⛈️", "⛈️"],
};
const wx = (code) => WEATHER[code] || ["", "❔", "❔"];
const icon = (code, isDay = 1) => wx(code)[isDay ? 1 : 2];

const $ = (id) => document.getElementById(id);
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);

function tick() {
  const now = new Date();
  $("clock").textContent = now.toLocaleTimeString(LOCALE, { hour: "2-digit", minute: "2-digit" });
  $("date").textContent = now.toLocaleDateString(LOCALE, { weekday: "long", day: "numeric", month: "long" });
}

function dayName(iso, i) {
  if (i === 0) return "Today";
  if (i === 1) return "Tomorrow";
  return new Date(iso + "T12:00").toLocaleDateString(LOCALE, { weekday: "long" });
}

function renderWeather(w) {
  if (!w) return;
  const c = w.current;
  $("now").innerHTML = `
    <div class="icon">${icon(c.code, c.is_day)}</div>
    <div class="temp">${c.temp}°</div>
    <div class="details">
      <b>${wx(c.code)[0]}</b><br>
      Feels like ${c.feels}° · ${c.wind} m/s<br>
      ${esc(w.location)}
    </div>`;

  $("hourly").innerHTML = w.hourly.filter((_, i) => i % 2 === 0).slice(0, 6).map((h) => `
    <div>
      <div class="h-time">${h.time}</div>
      <div class="h-icon">${icon(h.code, h.is_day)}</div>
      <div class="h-temp">${h.temp}°</div>
      <div class="h-rain">${h.precip >= 20 ? h.precip + "%" : ""}</div>
    </div>`).join("");

  $("daily").innerHTML = w.daily.slice(1, 6).map((d, i) => `
    <div class="d-row">
      <div class="d-name">${dayName(d.date, i + 1)}</div>
      <div class="d-icon">${icon(d.code)}</div>
      <div class="d-temp"><b>${d.max}°</b><span>${d.min}°</span></div>
      <div class="d-rain">${d.precip >= 20 ? d.precip + "%" : ""}</div>
    </div>`).join("");
}

function renderAgenda(a) {
  if (!a) return;
  const now = new Date();
  $("agenda").innerHTML = a.days.map((day, i) => {
    const date = new Date(day.date + "T12:00").toLocaleDateString(LOCALE, { day: "numeric", month: "short" });
    const events = day.events.map((e) => `
      <div class="event${!e.all_day && new Date(e.end_iso) < now ? " past" : ""}">
        <div class="time">${e.all_day ? "All day" : `${e.start}–${e.end}`}</div>
        <div class="bar" style="background:${esc(e.color)}"></div>
        <div class="title">${esc(e.title)}${e.location ? `<span class="where">${esc(e.location)}</span>` : ""}</div>
        <div class="who" style="background:${esc(e.color)}">${esc(e.person)}</div>
      </div>`).join("");
    return `
      <section class="day${i === 0 ? " today" : ""}">
        <div class="day-head">${dayName(day.date, i)}<span>${date}</span></div>
        ${events || `<div class="empty">Nothing planned</div>`}
      </section>`;
  }).join("");
}

async function refresh() {
  try {
    const s = await (await fetch("/api/state", { cache: "no-store" })).json();
    if (version && s.version !== version) location.reload(); // new deploy
    version = s.version;
    renderWeather(s.weather);
    renderAgenda(s.agenda);
    const errs = [...Object.entries(s.errors).map(([k, v]) => `${k}: ${v}`), ...(s.agenda?.errors || [])];
    $("errors").textContent = errs.join(" · ");
  } catch (err) {
    $("errors").textContent = "Can't reach the dashboard server";
  }
}

tick();
setInterval(tick, 1000);
refresh();
setInterval(refresh, 60 * 1000);
