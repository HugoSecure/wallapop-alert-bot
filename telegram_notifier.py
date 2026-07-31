import html
import logging

import requests

from config import CITY, REQUEST_TIMEOUT, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

logger = logging.getLogger(__name__)

API_URL = "https://api.telegram.org/bot{}/sendMessage"


def _fmt_money(value):
    s = f"{value:,.2f}"
    s = s.replace(",", "\x00").replace(".", ",").replace("\x00", ".")
    return f"{s} €"


def _fmt_age(age_minutes):
    if age_minutes < 60:
        return f"hace {int(age_minutes)} min"
    if age_minutes < 24 * 60:
        return f"hace {int(age_minutes / 60)} h"
    return f"hace {int(age_minutes / 1440)} d"


def build_message(title, price, city, distance_km, age_minutes, benefit, score, url):
    lines = [
        "🚨 OPORTUNIDAD DETECTADA",
        "",
        f"📦 <b>{html.escape(title)}</b>",
        f"💰 {_fmt_money(price)}",
        f"📍 {html.escape(city)}",
        f"📏 {distance_km:.1f} km a {html.escape(CITY)}",
        f"⏱️ {_fmt_age(age_minutes)}",
        f"📈 Beneficio estimado: +{_fmt_money(benefit)}",
        f"⭐ Puntuación: {score:.0f}/100",
        "",
        f'🔗 <a href="{html.escape(url, quote=True)}">Abrir anuncio</a>',
    ]
    return "\n".join(lines)


def send_telegram(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.error("Telegram no configurado: completa TELEGRAM_BOT_TOKEN y TELEGRAM_CHAT_ID en .env")
        return False
    try:
        resp = requests.post(
            API_URL.format(TELEGRAM_BOT_TOKEN),
            json={"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"},
            timeout=REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
        return resp.json().get("ok", False)
    except Exception as exc:
        logger.exception("Error enviando notificación de Telegram: %s", exc)
        return False
