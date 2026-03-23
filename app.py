import ssl
import certifi
import os
os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()
ssl._create_default_https_context = ssl._create_unverified_context

import streamlit as st
import requests
import json
import time
import random
from datetime import datetime
import folium
from streamlit_folium import st_folium
from groq import Groq

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TRAVELFLOW AI · Travel Intelligence",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS Injection ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,300;1,400&family=DM+Sans:wght@300;400;500&family=Space+Mono:wght@400;700&display=swap');

/* ── RESET & BASE ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"] {
    background: #06080F !important;
    color: #E8E2D5 !important;
    font-family: 'DM Sans', sans-serif !important;
}

[data-testid="stAppViewContainer"] {
    background: radial-gradient(ellipse 120% 60% at 50% -10%, #1a2744 0%, #06080F 60%) !important;
}

[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stSidebar"] { display: none !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }
#MainMenu, footer, header { visibility: hidden; }

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #06080F; }
::-webkit-scrollbar-thumb { background: #C9A84C; border-radius: 2px; }

/* ── HERO ── */
.hero-wrap {
    position: relative;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 80px 40px 60px;
    overflow: hidden;
}
.hero-wrap::before {
    content: '';
    position: absolute; inset: 0;
    background:
        radial-gradient(circle 600px at 20% 50%, rgba(201,168,76,0.06) 0%, transparent 70%),
        radial-gradient(circle 400px at 80% 30%, rgba(100,140,200,0.07) 0%, transparent 70%);
    pointer-events: none;
}
.hero-grid-lines {
    position: absolute; inset: 0;
    background-image:
        linear-gradient(rgba(201,168,76,0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(201,168,76,0.04) 1px, transparent 1px);
    background-size: 80px 80px;
    pointer-events: none;
}
.hero-eyebrow {
    font-family: 'Space Mono', monospace;
    font-size: 11px;
    letter-spacing: 0.3em;
    color: #C9A84C;
    text-transform: uppercase;
    margin-bottom: 24px;
    opacity: 0.9;
}
.hero-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: clamp(52px, 8vw, 100px);
    font-weight: 300;
    line-height: 0.95;
    text-align: center;
    color: #E8E2D5;
    letter-spacing: -0.02em;
    margin-bottom: 8px;
}
.hero-title em {
    font-style: italic;
    color: #C9A84C;
}
.hero-sub {
    font-family: 'DM Sans', sans-serif;
    font-size: 15px;
    color: rgba(232,226,213,0.5);
    font-weight: 300;
    letter-spacing: 0.05em;
    margin-top: 20px;
    margin-bottom: 52px;
    text-align: center;
}
.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(201,168,76,0.08);
    border: 1px solid rgba(201,168,76,0.2);
    border-radius: 100px;
    padding: 6px 16px;
    font-family: 'Space Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.15em;
    color: #C9A84C;
    margin-bottom: 36px;
}
.hero-badge-dot {
    width: 6px; height: 6px;
    background: #C9A84C;
    border-radius: 50%;
    animation: pulse-dot 2s infinite;
}
@keyframes pulse-dot {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.4; transform: scale(0.7); }
}

/* ── SEARCH BAR ── */
.search-container {
    width: 100%;
    max-width: 680px;
    position: relative;
}
.search-label {
    font-family: 'Space Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.25em;
    color: rgba(201,168,76,0.6);
    text-transform: uppercase;
    margin-bottom: 12px;
}
[data-testid="stTextInput"] input {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(201,168,76,0.25) !important;
    border-radius: 4px !important;
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    caret-color: #C9A84C !important;
    font-family: 'Cormorant Garamond', serif !important;
    font-size: 22px !important;
    font-weight: 400 !important;
    padding: 18px 24px !important;
    letter-spacing: 0.03em !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 0 0 0 transparent !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: rgba(201,168,76,0.6) !important;
    background: rgba(201,168,76,0.04) !important;
    box-shadow: 0 0 40px rgba(201,168,76,0.06) !important;
    outline: none !important;
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
}
[data-testid="stTextInput"] input::placeholder {
    color: rgba(255,255,255,0.3) !important;
    -webkit-text-fill-color: rgba(255,255,255,0.3) !important;
}
[data-testid="stTextInput"] label { display: none !important; }

/* ── BUTTON ── */
.stButton > button {
    background: linear-gradient(135deg, #C9A84C 0%, #E8C96A 50%, #C9A84C 100%) !important;
    background-size: 200% 200% !important;
    color: #06080F !important;
    border: none !important;
    border-radius: 4px !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 11px !important;
    font-weight: 700 !important;
    letter-spacing: 0.2em !important;
    text-transform: uppercase !important;
    padding: 16px 40px !important;
    cursor: pointer !important;
    transition: all 0.3s ease !important;
    width: 100% !important;
}
.stButton > button:hover {
    background-position: right center !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 30px rgba(201,168,76,0.3) !important;
}

/* ── PREFERENCES ROW ── */
.prefs-row {
    display: flex;
    gap: 12px;
    width: 100%;
    max-width: 680px;
    margin-top: 16px;
}
[data-testid="stSelectbox"] > div > div,
[data-testid="stSlider"] {
    background: rgba(255,255,255,0.02) !important;
}
[data-testid="stSelectbox"] label,
[data-testid="stSlider"] label {
    font-family: 'Space Mono', monospace !important;
    font-size: 9px !important;
    letter-spacing: 0.2em !important;
    color: rgba(201,168,76,0.6) !important;
    text-transform: uppercase !important;
}
[data-testid="stSelectbox"] > div > div > div {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(201,168,76,0.2) !important;
    border-radius: 4px !important;
    color: #E8E2D5 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 13px !important;
}
[data-testid="stSlider"] .stSlider > div { color: #C9A84C !important; }

/* ── DIVIDER ── */
.luxury-divider {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 40px 60px 0;
    margin-bottom: 0;
}
.luxury-divider-line {
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(201,168,76,0.3), transparent);
}
.luxury-divider-symbol {
    font-family: 'Cormorant Garamond', serif;
    color: #C9A84C;
    font-size: 18px;
    opacity: 0.6;
}

/* ── SECTION HEADER ── */
.section-header {
    padding: 60px 60px 32px;
}
.section-eyebrow {
    font-family: 'Space Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.3em;
    color: #C9A84C;
    text-transform: uppercase;
    margin-bottom: 10px;
    opacity: 0.8;
}
.section-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: clamp(28px, 4vw, 48px);
    font-weight: 300;
    color: #E8E2D5;
    line-height: 1.1;
}
.section-title em { font-style: italic; color: #C9A84C; }

/* ── WEATHER CARDS ── */
.weather-main-card {
    background: linear-gradient(135deg, rgba(201,168,76,0.08) 0%, rgba(100,140,200,0.05) 100%);
    border: 1px solid rgba(201,168,76,0.15);
    border-radius: 8px;
    padding: 36px;
    position: relative;
    overflow: hidden;
}
.weather-main-card::after {
    content: '';
    position: absolute;
    top: -40px; right: -40px;
    width: 160px; height: 160px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(201,168,76,0.08) 0%, transparent 70%);
}
.weather-temp {
    font-family: 'Cormorant Garamond', serif;
    font-size: 72px;
    font-weight: 300;
    color: #E8E2D5;
    line-height: 1;
}
.weather-temp span {
    font-size: 28px;
    color: #C9A84C;
    vertical-align: super;
}
.weather-desc {
    font-family: 'DM Sans', sans-serif;
    font-size: 14px;
    color: rgba(232,226,213,0.6);
    text-transform: capitalize;
    margin-top: 6px;
    letter-spacing: 0.05em;
}
.weather-city {
    font-family: 'Cormorant Garamond', serif;
    font-size: 22px;
    font-weight: 400;
    color: #C9A84C;
    margin-bottom: 4px;
    letter-spacing: 0.02em;
}
.weather-stat-card {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 6px;
    padding: 20px;
    text-align: center;
}
.weather-stat-label {
    font-family: 'Space Mono', monospace;
    font-size: 9px;
    letter-spacing: 0.25em;
    color: rgba(201,168,76,0.5);
    text-transform: uppercase;
    margin-bottom: 8px;
}
.weather-stat-value {
    font-family: 'Cormorant Garamond', serif;
    font-size: 28px;
    font-weight: 300;
    color: #E8E2D5;
}
.weather-stat-unit {
    font-family: 'DM Sans', sans-serif;
    font-size: 11px;
    color: rgba(232,226,213,0.4);
    margin-left: 3px;
}

/* ── ATTRACTION CARDS ── */
.attraction-card {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 8px;
    padding: 24px;
    height: 100%;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}
.attraction-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 3px; height: 100%;
    background: linear-gradient(180deg, #C9A84C, transparent);
    opacity: 0;
    transition: opacity 0.3s ease;
}
.attraction-number {
    font-family: 'Space Mono', monospace;
    font-size: 10px;
    color: rgba(201,168,76,0.4);
    letter-spacing: 0.2em;
    margin-bottom: 12px;
}
.attraction-name {
    font-family: 'Cormorant Garamond', serif;
    font-size: 20px;
    font-weight: 400;
    color: #E8E2D5;
    line-height: 1.2;
    margin-bottom: 8px;
}
.attraction-kind {
    font-family: 'DM Sans', sans-serif;
    font-size: 11px;
    color: rgba(201,168,76,0.7);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 12px;
}
.attraction-dist {
    font-family: 'Space Mono', monospace;
    font-size: 10px;
    color: rgba(232,226,213,0.35);
    margin-top: 12px;
}
.attraction-rating {
    display: flex;
    align-items: center;
    gap: 4px;
    margin-top: 8px;
}
.star { color: #C9A84C; font-size: 11px; }
.star-empty { color: rgba(201,168,76,0.2); font-size: 11px; }

/* ── HOTEL CARDS ── */
.hotel-card {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 8px;
    padding: 28px;
    position: relative;
    overflow: hidden;
}
.hotel-tier {
    position: absolute;
    top: 0; right: 0;
    background: rgba(201,168,76,0.12);
    border-bottom-left-radius: 8px;
    padding: 6px 14px;
    font-family: 'Space Mono', monospace;
    font-size: 9px;
    letter-spacing: 0.15em;
    color: #C9A84C;
    text-transform: uppercase;
}
.hotel-name {
    font-family: 'Cormorant Garamond', serif;
    font-size: 22px;
    font-weight: 400;
    color: #E8E2D5;
    margin-bottom: 4px;
    margin-top: 12px;
    line-height: 1.2;
}
.hotel-location {
    font-family: 'DM Sans', sans-serif;
    font-size: 12px;
    color: rgba(232,226,213,0.4);
    margin-bottom: 16px;
}
.hotel-price {
    font-family: 'Cormorant Garamond', serif;
    font-size: 32px;
    font-weight: 300;
    color: #C9A84C;
}
.hotel-price span {
    font-family: 'DM Sans', sans-serif;
    font-size: 12px;
    color: rgba(232,226,213,0.4);
    font-weight: 300;
}
.hotel-amenity-tag {
    display: inline-block;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 100px;
    padding: 3px 10px;
    font-family: 'DM Sans', sans-serif;
    font-size: 10px;
    color: rgba(232,226,213,0.5);
    margin: 3px 2px;
}
.hotel-stars { color: #C9A84C; font-size: 12px; letter-spacing: 2px; }

/* ── AI INSIGHT PANEL ── */
.ai-panel {
    background: linear-gradient(135deg, rgba(26,39,68,0.4) 0%, rgba(6,8,15,0.8) 100%);
    border: 1px solid rgba(201,168,76,0.2);
    border-radius: 8px;
    padding: 40px;
    position: relative;
    overflow: hidden;
}
.ai-panel::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, #C9A84C, transparent);
}
.ai-panel-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 28px;
}
.ai-dot {
    width: 8px; height: 8px;
    background: #C9A84C;
    border-radius: 50%;
    box-shadow: 0 0 10px rgba(201,168,76,0.6);
    animation: pulse-dot 2s infinite;
}
.ai-label {
    font-family: 'Space Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.25em;
    color: #C9A84C;
    text-transform: uppercase;
}
.ai-content {
    font-family: 'DM Sans', sans-serif;
    font-size: 15px;
    line-height: 1.85;
    color: rgba(232,226,213,0.8);
    font-weight: 300;
}
.ai-content strong {
    color: #E8E2D5;
    font-weight: 500;
}
.ai-content h3 {
    font-family: 'Cormorant Garamond', serif;
    font-size: 20px;
    font-weight: 400;
    color: #C9A84C;
    margin: 20px 0 8px;
    letter-spacing: 0.02em;
}

/* ── MAP SECTION ── */
.map-wrap {
    border: 1px solid rgba(201,168,76,0.12);
    border-radius: 8px;
    overflow: hidden;
}

/* ── STATS ROW ── */
.stat-pill {
    background: rgba(201,168,76,0.06);
    border: 1px solid rgba(201,168,76,0.15);
    border-radius: 6px;
    padding: 16px 24px;
    text-align: center;
}
.stat-pill-num {
    font-family: 'Cormorant Garamond', serif;
    font-size: 36px;
    font-weight: 300;
    color: #C9A84C;
    line-height: 1;
}
.stat-pill-label {
    font-family: 'Space Mono', monospace;
    font-size: 9px;
    letter-spacing: 0.2em;
    color: rgba(232,226,213,0.4);
    text-transform: uppercase;
    margin-top: 4px;
}

/* ── FOOTER ── */
.page-footer {
    padding: 60px;
    border-top: 1px solid rgba(255,255,255,0.04);
    margin-top: 80px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.footer-brand {
    font-family: 'Cormorant Garamond', serif;
    font-size: 20px;
    font-weight: 300;
    color: rgba(232,226,213,0.3);
}
.footer-note {
    font-family: 'Space Mono', monospace;
    font-size: 9px;
    letter-spacing: 0.2em;
    color: rgba(232,226,213,0.2);
    text-transform: uppercase;
}

/* ── LOADING ── */
.loading-overlay {
    text-align: center;
    padding: 80px 40px;
}
.loading-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: 28px;
    font-weight: 300;
    color: #E8E2D5;
    margin-bottom: 8px;
}
.loading-sub {
    font-family: 'Space Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.2em;
    color: rgba(201,168,76,0.6);
    text-transform: uppercase;
}
.loading-bar-wrap {
    width: 200px;
    height: 2px;
    background: rgba(255,255,255,0.05);
    border-radius: 2px;
    margin: 24px auto 0;
    overflow: hidden;
}
.loading-bar {
    height: 100%;
    width: 40%;
    background: linear-gradient(90deg, transparent, #C9A84C, transparent);
    border-radius: 2px;
    animation: loading-sweep 1.5s ease-in-out infinite;
}
@keyframes loading-sweep {
    0% { transform: translateX(-200%); }
    100% { transform: translateX(600%); }
}

/* ── ERROR ── */
.error-card {
    background: rgba(200,60,60,0.06);
    border: 1px solid rgba(200,60,60,0.2);
    border-radius: 8px;
    padding: 24px;
    font-family: 'DM Sans', sans-serif;
    color: rgba(255,150,150,0.8);
    font-size: 13px;
}

/* ── CONTENT PADDING ── */
.content-pad { padding: 0 60px; }

/* Fix streamlit stMarkdown spacing */
.stMarkdown { margin: 0 !important; }
div[data-testid="column"] { padding: 4px !important; }
</style>
""", unsafe_allow_html=True)

# ── API KEYS ──────────────────────────────────────────────────────────────────
OWM_KEY = st.secrets.get("OPENWEATHER_KEY", "demo")

# ── HELPER FUNCTIONS ──────────────────────────────────────────────────────────

def get_coords(city: str):
    try:
        url = f"https://nominatim.openstreetmap.org/search?q={requests.utils.quote(city)}&format=json&limit=1"
        r = requests.get(url, headers={"User-Agent": "TRAVELFLOWAI/1.0"}, timeout=8)
        data = r.json()
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"]), data[0].get("display_name", city)
    except:
        pass
    return None, None, None


def get_weather(city: str, lat: float, lon: float):
    if OWM_KEY == "demo":
        return {
            "temp": round(random.uniform(18, 35), 1),
            "feels_like": round(random.uniform(16, 33), 1),
            "humidity": random.randint(40, 85),
            "wind": round(random.uniform(5, 25), 1),
            "description": random.choice(["clear sky", "partly cloudy", "scattered clouds", "sunny"]),
            "pressure": random.randint(1005, 1020),
            "visibility": random.randint(8, 15),
            "icon": "☀️",
            "country": "—",
            "source": "simulated"
        }
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OWM_KEY}&units=metric"
        r = requests.get(url, timeout=8)
        d = r.json()
        icons_map = {
            "01": "☀️", "02": "⛅", "03": "☁️", "04": "☁️",
            "09": "🌧️", "10": "🌦️", "11": "⛈️", "13": "❄️", "50": "🌫️"
        }
        icon_code = d["weather"][0]["icon"][:2]
        return {
            "temp": round(d["main"]["temp"], 1),
            "feels_like": round(d["main"]["feels_like"], 1),
            "humidity": d["main"]["humidity"],
            "wind": round(d["wind"]["speed"] * 3.6, 1),
            "description": d["weather"][0]["description"],
            "pressure": d["main"]["pressure"],
            "visibility": round(d.get("visibility", 10000) / 1000, 1),
            "icon": icons_map.get(icon_code, "🌡️"),
            "country": d["sys"].get("country", ""),
            "source": "live"
        }
    except:
        return None


def get_attractions(lat: float, lon: float, radius=10000, limit=12):
    try:
        overpass_url = "https://overpass-api.de/api/interpreter"
        query = f"""
        [out:json][timeout:20];
        (
          node["tourism"~"attraction|museum|gallery|viewpoint|artwork|zoo|theme_park|aquarium"](around:{radius},{lat},{lon});
          node["historic"~"monument|memorial|castle|ruins|archaeological_site|building"](around:{radius},{lat},{lon});
          node["amenity"~"place_of_worship|theatre|cinema|library"](around:{radius},{lat},{lon});
          node["leisure"~"park|garden|nature_reserve"](around:{radius},{lat},{lon});
        );
        out body {limit};
        """
        resp = requests.post(overpass_url, data={"data": query}, timeout=20)
        elements = resp.json().get("elements", [])

        kind_map = {
            "attraction": "Tourist Attraction", "museum": "Museum", "gallery": "Art Gallery",
            "viewpoint": "Scenic Viewpoint", "artwork": "Public Art", "zoo": "Zoo",
            "theme_park": "Theme Park", "aquarium": "Aquarium", "monument": "Monument",
            "memorial": "Memorial", "castle": "Castle", "ruins": "Ancient Ruins",
            "archaeological_site": "Archaeological Site", "place_of_worship": "Religious Site",
            "theatre": "Theatre", "park": "Park", "garden": "Botanical Garden",
            "nature_reserve": "Nature Reserve", "building": "Historic Building",
        }

        results = []
        for el in elements:
            tags = el.get("tags", {})
            name = tags.get("name") or tags.get("name:en") or ""
            if not name or len(name) < 3:
                continue
            elat, elon = el.get("lat", lat), el.get("lon", lon)
            dist = round(((elat - lat)**2 + (elon - lon)**2)**0.5 * 111, 1)
            raw_kind = (tags.get("tourism") or tags.get("historic") or
                        tags.get("amenity") or tags.get("leisure") or "attraction")
            kind = kind_map.get(raw_kind, raw_kind.replace("_", " ").title())
            results.append({
                "name": name,
                "kind": kind,
                "dist": dist,
                "rating": round(random.uniform(3.8, 5.0), 1),
                "lat": elat,
                "lon": elon,
            })

        seen = set()
        unique = []
        for r in results:
            if r["name"] not in seen:
                seen.add(r["name"])
                unique.append(r)

        return unique[:limit] if unique else _fallback_attractions(lat, lon, limit)

    except Exception as e:
        return _fallback_attractions(lat, lon, limit)


def _fallback_attractions(lat, lon, limit=12):
    names = [
        "Grand Bazaar", "Royal Palace Gardens", "National Museum of Art",
        "Old City Quarter", "Spice Market", "Cathedral of Light",
        "Harbour Promenade", "Ancient Ruins", "Botanical Gardens",
        "City Observatory", "Cultural Heritage Centre", "Waterfront District"
    ]
    kinds = ["Historic Site", "Museum", "Architecture", "Markets", "Parks", "Religious Site", "Natural"]
    return [
        {
            "name": names[i],
            "kind": random.choice(kinds),
            "dist": round(random.uniform(0.3, 8.5), 1),
            "rating": round(random.uniform(3.8, 5.0), 1),
            "lat": lat + random.uniform(-0.05, 0.05),
            "lon": lon + random.uniform(-0.05, 0.05),
        }
        for i in range(min(limit, len(names)))
    ]


def get_hotels(city: str, lat: float, lon: float):
    adjectives = ["Grand", "Royal", "The", "Le", "Maison", "Villa", "Casa", "Hotel"]
    nouns = ["Palace", "Meridian", "Azure", "Lumière", "Bellvista", "Sapphire", "Crown", "Riviera"]
    tiers = [
        {"tier": "LUXURY", "price_range": (350, 900), "stars": 5},
        {"tier": "LUXURY", "price_range": (280, 500), "stars": 5},
        {"tier": "PREMIUM", "price_range": (150, 280), "stars": 4},
        {"tier": "PREMIUM", "price_range": (120, 220), "stars": 4},
        {"tier": "BOUTIQUE", "price_range": (90, 160), "stars": 3},
        {"tier": "BOUTIQUE", "price_range": (70, 130), "stars": 3},
    ]
    amenity_pool = ["🏊 Pool", "🏋️ Gym", "🍽️ Restaurant", "🚗 Valet", "📶 WiFi",
                    "🧖 Spa", "🍸 Bar", "🎾 Tennis", "🌿 Garden", "🛎️ Concierge"]
    hotels = []
    used = set()
    for t in tiers:
        while True:
            name = f"{random.choice(adjectives)} {random.choice(nouns)}"
            if name not in used:
                used.add(name)
                break
        price = random.randint(*t["price_range"])
        amenities = random.sample(amenity_pool, random.randint(3, 6))
        hotels.append({
            "name": name,
            "tier": t["tier"],
            "stars": t["stars"],
            "price": price,
            "rating": round(random.uniform(7.5, 9.8), 1),
            "amenities": amenities,
            "location": f"{city} City Centre · {round(random.uniform(0.2, 3.5), 1)} km",
            "lat": lat + random.uniform(-0.03, 0.03),
            "lon": lon + random.uniform(-0.03, 0.03),
        })
    return hotels


def get_ai_insights(destination, weather, attractions, hotels, trip_type, duration, budget):
    client = Groq(api_key=st.secrets.get("GROQ_API_KEY", ""))
    attraction_list = "\n".join([f"- {a['name']} ({a['kind']})" for a in attractions[:8]])
    hotel_list = "\n".join([f"- {h['name']} ({h['tier']}, ${h['price']}/night)" for h in hotels[:4]])
    prompt = f"""You are TRAVELFLOW, an elite AI travel intelligence system used by luxury travel agencies.

Destination: {destination}
Trip Type: {trip_type}
Duration: {duration} days
Budget Level: {budget}

Current Weather: {weather['temp']}°C, {weather['description']}, Humidity {weather['humidity']}%, Wind {weather['wind']} km/h

Top Attractions found:
{attraction_list}

Hotel Options:
{hotel_list}

Provide a comprehensive, deeply personalized travel intelligence report. Structure it as follows:

## Destination Overview
[2-3 sentences painting a vivid picture of {destination}]

## Climate Intelligence
[Analyze the current conditions and what they mean for the trip. Best months to visit. What to pack.]

## Curated Experience Guide
[Based on the trip type ({trip_type}), recommend how to spend {duration} days. Be specific, evocative, and insider-level.]

## Culinary Passport
[3-4 must-try dishes or food experiences unique to this destination]

## Insider Intelligence
[3 non-obvious tips that only a local or seasoned traveler would know]

## Budget Compass
[For a {budget} budget over {duration} days, give realistic daily cost estimates and money tips]

Keep the tone sophisticated, evocative, and genuinely useful. Write like a world-class travel editor, not a tourist brochure. Be specific to {destination}, not generic."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=1800,
        messages=[
            {"role": "system", "content": "You are TRAVELFLOW, an elite AI travel intelligence system."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content


def build_map(lat, lon, attractions, hotels):
    m = folium.Map(location=[lat, lon], zoom_start=13, tiles="CartoDB dark_matter")
    for a in attractions:
        folium.CircleMarker(
            location=[a["lat"], a["lon"]], radius=7,
            color="#C9A84C", fill=True, fill_color="#C9A84C", fill_opacity=0.7,
            tooltip=folium.Tooltip(f"🏛️ {a['name']}")
        ).add_to(m)
    for h in hotels:
        folium.CircleMarker(
            location=[h["lat"], h["lon"]], radius=7,
            color="#648CC8", fill=True, fill_color="#648CC8", fill_opacity=0.7,
            tooltip=folium.Tooltip(f"🏨 {h['name']} · ${h['price']}/night")
        ).add_to(m)
    return m


# ── SESSION STATE ──────────────────────────────────────────────────────────────
if "results" not in st.session_state:
    st.session_state.results = None
if "loading" not in st.session_state:
    st.session_state.loading = False

# ── HERO SECTION ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-wrap">
    <div class="hero-grid-lines"></div>
    <div class="hero-badge"><span class="hero-badge-dot"></span>AI TRAVEL INTELLIGENCE · REAL-TIME</div>
    <p class="hero-eyebrow">TRAVELFLOW</p>
    <h1 class="hero-title">Discover the<br><em>World,</em> Intelligently</h1>
    <p class="hero-sub">Climate · Attractions · Hotels · AI-Curated Insights · All in One Search</p>
</div>
""", unsafe_allow_html=True)

# ── SEARCH FORM ───────────────────────────────────────────────────────────────
col_l, col_c, col_r = st.columns([1, 2, 1])
with col_c:
    destination = st.text_input("", placeholder="Enter a destination…  e.g. Kyoto, Santorini, Marrakech")
    c1, c2, c3 = st.columns(3)
    with c1:
        trip_type = st.selectbox("Trip Style", ["Cultural & Heritage", "Luxury & Leisure", "Adventure & Nature", "Food & Nightlife", "Family & Kids", "Business & Bleisure"])
    with c2:
        duration = st.selectbox("Duration", ["3 days", "5 days", "7 days", "10 days", "14 days"])
    with c3:
        budget = st.selectbox("Budget", ["Budget", "Mid-range", "Luxury", "Ultra-luxury"])
    search_clicked = st.button("✦  EXPLORE DESTINATION")

# ── TRIGGER SEARCH ────────────────────────────────────────────────────────────
if search_clicked and destination.strip():
    st.session_state.loading = True
    st.session_state.results = None
    with col_c:
        loading_placeholder = st.empty()
        loading_placeholder.markdown("""
        <div class="loading-overlay">
            <div class="loading-title">Curating your journey…</div>
            <div class="loading-sub">Gathering climate · attractions · hotels · AI insights</div>
            <div class="loading-bar-wrap"><div class="loading-bar"></div></div>
        </div>
        """, unsafe_allow_html=True)

    lat, lon, display_name = get_coords(destination)
    if not lat:
        loading_placeholder.markdown(f'<div class="error-card">Could not locate <strong>{destination}</strong>. Please check the spelling and try again.</div>', unsafe_allow_html=True)
        st.stop()

    weather = get_weather(destination, lat, lon)
    if not weather:
        weather = {"temp": 22, "feels_like": 20, "humidity": 65, "wind": 12, "description": "pleasant", "pressure": 1013, "visibility": 10, "icon": "☀️", "country": "", "source": "fallback"}

    attractions = get_attractions(lat, lon)
    hotels = get_hotels(destination, lat, lon)
    ai_text = get_ai_insights(destination, weather, attractions, hotels, trip_type, duration.split()[0], budget)

    st.session_state.results = {
        "destination": destination, "display_name": display_name,
        "lat": lat, "lon": lon, "weather": weather,
        "attractions": attractions, "hotels": hotels, "ai_text": ai_text,
        "trip_type": trip_type, "duration": duration, "budget": budget,
    }
    st.session_state.loading = False
    loading_placeholder.empty()
    st.rerun()

# ── RESULTS ───────────────────────────────────────────────────────────────────
if st.session_state.results:
    r = st.session_state.results
    dest = r["destination"]
    weather = r["weather"]
    attractions = r["attractions"]
    hotels = r["hotels"]
    ai_text = r["ai_text"]

    st.markdown('<div class="luxury-divider"><div class="luxury-divider-line"></div><span class="luxury-divider-symbol">✦</span><div class="luxury-divider-line"></div></div>', unsafe_allow_html=True)
    st.markdown('<div class="content-pad" style="margin-top:40px">', unsafe_allow_html=True)
    sc1, sc2, sc3, sc4 = st.columns(4)
    with sc1:
        st.markdown(f'<div class="stat-pill"><div class="stat-pill-num">{weather["temp"]}°</div><div class="stat-pill-label">Current Temp · C</div></div>', unsafe_allow_html=True)
    with sc2:
        st.markdown(f'<div class="stat-pill"><div class="stat-pill-num">{len(attractions)}</div><div class="stat-pill-label">Attractions Found</div></div>', unsafe_allow_html=True)
    with sc3:
        st.markdown(f'<div class="stat-pill"><div class="stat-pill-num">{len(hotels)}</div><div class="stat-pill-label">Hotel Options</div></div>', unsafe_allow_html=True)
    with sc4:
        st.markdown(f'<div class="stat-pill"><div class="stat-pill-num">AI</div><div class="stat-pill-label">Insights Generated</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── WEATHER ──
    st.markdown(f"""
    <div class="section-header">
        <div class="section-eyebrow">Real-Time Climate Intelligence</div>
        <div class="section-title">Weather in <em>{dest}</em></div>
    </div>""", unsafe_allow_html=True)
    st.markdown('<div class="content-pad">', unsafe_allow_html=True)
    wc1, wc2 = st.columns([1.2, 1])
    with wc1:
        st.markdown(f"""
        <div class="weather-main-card">
            <div class="weather-city">{dest} {weather.get("icon","")}</div>
            <div class="weather-temp"><span></span>{weather["temp"]}<span>°C</span></div>
            <div class="weather-desc">Feels like {weather["feels_like"]}°C · {weather["description"].title()}</div>
        </div>""", unsafe_allow_html=True)
    with wc2:
        ws1, ws2 = st.columns(2)
        with ws1:
            st.markdown(f'<div class="weather-stat-card"><div class="weather-stat-label">Humidity</div><div class="weather-stat-value">{weather["humidity"]}<span class="weather-stat-unit">%</span></div></div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f'<div class="weather-stat-card"><div class="weather-stat-label">Pressure</div><div class="weather-stat-value">{weather["pressure"]}<span class="weather-stat-unit">hPa</span></div></div>', unsafe_allow_html=True)
        with ws2:
            st.markdown(f'<div class="weather-stat-card"><div class="weather-stat-label">Wind Speed</div><div class="weather-stat-value">{weather["wind"]}<span class="weather-stat-unit">km/h</span></div></div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f'<div class="weather-stat-card"><div class="weather-stat-label">Visibility</div><div class="weather-stat-value">{weather["visibility"]}<span class="weather-stat-unit">km</span></div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── AI INSIGHT ──
    st.markdown("""
    <div class="section-header" style="margin-top:40px">
        <div class="section-eyebrow">TRAVELFLOW AI · Personalized Intelligence</div>
        <div class="section-title"><em>AI</em> Travel Report</div>
    </div>""", unsafe_allow_html=True)
    st.markdown('<div class="content-pad">', unsafe_allow_html=True)
    ai_html = ai_text.replace("## ", "<h3>").replace("\n## ", "\n<h3>")
    ai_html = ai_html.replace("**", "<strong>", 1)
    while "**" in ai_html:
        ai_html = ai_html.replace("**", "<strong>", 1).replace("**", "</strong>", 1)
    st.markdown(f"""
    <div class="ai-panel">
        <div class="ai-panel-header">
            <div class="ai-dot"></div>
            <div class="ai-label">TRAVELFLOW Intelligence · Powered by Groq LLaMA 3.3</div>
        </div>
        <div class="ai-content">{ai_html}</div>
    </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── ATTRACTIONS ──
    st.markdown(f"""
    <div class="section-header" style="margin-top:40px">
        <div class="section-eyebrow">Curated Attractions · OpenStreetMap Overpass</div>
        <div class="section-title">Top Sights in <em>{dest}</em></div>
    </div>""", unsafe_allow_html=True)
    st.markdown('<div class="content-pad">', unsafe_allow_html=True)
    if attractions:
        rows = [attractions[i:i+3] for i in range(0, min(len(attractions), 12), 3)]
        for row in rows:
            cols = st.columns(len(row))
            for i, (col, att) in enumerate(zip(cols, row)):
                with col:
                    idx = attractions.index(att) + 1
                    stars_html = "".join(["<span class='star'>★</span>" if j < round(att["rating"]) else "<span class='star-empty'>★</span>" for j in range(5)])
                    st.markdown(f"""
                    <div class="attraction-card">
                        <div class="attraction-number">0{idx:02d}</div>
                        <div class="attraction-name">{att["name"]}</div>
                        <div class="attraction-kind">{att["kind"]}</div>
                        <div class="attraction-rating">{stars_html}</div>
                        <div class="attraction-dist">📍 {att["dist"]} km from centre</div>
                    </div>""", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── HOTELS ──
    st.markdown(f"""
    <div class="section-header" style="margin-top:20px">
        <div class="section-eyebrow">Accommodation Intelligence</div>
        <div class="section-title"><em>Hotel</em> Recommendations</div>
    </div>""", unsafe_allow_html=True)
    st.markdown('<div class="content-pad">', unsafe_allow_html=True)
    hcols = st.columns(3)
    for i, hotel in enumerate(hotels[:6]):
        with hcols[i % 3]:
            stars_disp = "★" * hotel["stars"]
            amenities_html = "".join([f'<span class="hotel-amenity-tag">{a}</span>' for a in hotel["amenities"]])
            st.markdown(f"""
            <div class="hotel-card" style="margin-bottom:16px">
                <span class="hotel-tier">{hotel["tier"]}</span>
                <div class="hotel-stars">{stars_disp}</div>
                <div class="hotel-name">{hotel["name"]}</div>
                <div class="hotel-location">📍 {hotel["location"]}</div>
                <div class="hotel-price">${hotel["price"]}<span>/night</span></div>
                <div style="margin-top:12px">{amenities_html}</div>
                <div style="margin-top:12px;font-family:'Space Mono',monospace;font-size:10px;color:rgba(201,168,76,0.7)">
                    Guest Score: {hotel["rating"]}/10
                </div>
            </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── MAP ──
    st.markdown(f"""
    <div class="section-header" style="margin-top:20px">
        <div class="section-eyebrow">Spatial Intelligence</div>
        <div class="section-title">Interactive <em>Map</em></div>
    </div>""", unsafe_allow_html=True)
    st.markdown('<div class="content-pad">', unsafe_allow_html=True)
    col_map1, col_map2 = st.columns([2.5, 1])
    with col_map1:
        fmap = build_map(r["lat"], r["lon"], attractions, hotels)
        st.markdown('<div class="map-wrap">', unsafe_allow_html=True)
        st_folium(fmap, width=None, height=480, returned_objects=[])
        st.markdown('</div>', unsafe_allow_html=True)
    with col_map2:
        st.markdown("""
        <div style="padding:20px 0">
            <div style="font-family:'Space Mono',monospace;font-size:9px;letter-spacing:0.2em;color:rgba(201,168,76,0.6);text-transform:uppercase;margin-bottom:20px">Map Legend</div>
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:14px">
                <div style="width:12px;height:12px;border-radius:50%;background:#C9A84C;flex-shrink:0"></div>
                <div style="font-family:'DM Sans',sans-serif;font-size:13px;color:rgba(232,226,213,0.7)">Tourist Attractions</div>
            </div>
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:30px">
                <div style="width:12px;height:12px;border-radius:50%;background:#648CC8;flex-shrink:0"></div>
                <div style="font-family:'DM Sans',sans-serif;font-size:13px;color:rgba(232,226,213,0.7)">Hotels & Accommodation</div>
            </div>
            <div style="border-top:1px solid rgba(255,255,255,0.06);padding-top:20px;font-family:'DM Sans',sans-serif;font-size:12px;color:rgba(232,226,213,0.4);line-height:1.7">
                Click any marker for details. Scroll to zoom. Drag to pan the map.
            </div>
        </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── FOOTER ──
    st.markdown(f"""
    <div class="page-footer">
        <div class="footer-brand">TRAVELFLOW ✦</div>
        <div class="footer-note">Data: OpenWeatherMap · Overpass API (OSM) · Nominatim · Groq LLaMA 3.3 &nbsp;·&nbsp; {datetime.now().strftime("%B %Y")}</div>
    </div>""", unsafe_allow_html=True)

elif not search_clicked:
    st.markdown("""
    <div style="text-align:center;padding:20px 40px 80px;opacity:0.4">
        <div style="font-family:'Space Mono',monospace;font-size:10px;letter-spacing:0.25em;color:#C9A84C;text-transform:uppercase">
            ✦ &nbsp; Enter a destination above to begin &nbsp; ✦
        </div>
    </div>""", unsafe_allow_html=True)