import argparse
import logging
import time

from config import (
    CHECK_INTERVAL,
    DEEP_SCAN_INTERVAL,
    DEEP_SCAN_RESULTS,
    MAX_PRICE,
    MAX_RESULTS,
    MIN_PRICE,
    MIN_SCORE_TO_NOTIFY,
    RADIUS_KM,
    SEARCH_KEYWORDS,
    SKIP_RESERVED,
)
from geolocation import distance_to_motril
from scoring import compute_score
from storage import is_new, mark_seen
from telegram_notifier import build_message, send_telegram
from wallapop import WallapopClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("main")


def _ad_price(ad):
    price = ad.get("price")
    if isinstance(price, dict):
        return price.get("amount") or 0
    return price or 0


def _ad_city(ad):
    location = ad.get("location") or {}
    return location.get("city") or location.get("region") or "Desconocida"


def _ad_coords(ad):
    location = ad.get("location") or {}
    lat = location.get("latitude")
    lng = location.get("longitude")
    if lat is None or lng is None:
        return None
    return float(lat), float(lng)


def _ad_age_minutes(ad):
    ts = ad.get("created_at") or ad.get("modified_at") or 0
    try:
        created = float(ts)
    except (TypeError, ValueError):
        return 0.0
    if created > 1e11:
        created /= 1000.0
    return max(0.0, (time.time() - created) / 60)


def _ad_url(ad):
    slug = ad.get("web_slug")
    if slug:
        return f"https://es.wallapop.com/item/{slug}"
    return f"https://es.wallapop.com/item/{ad.get('id', '')}"


def _is_reserved(ad):
    reserved = ad.get("reserved")
    if isinstance(reserved, dict):
        return bool(reserved.get("flag"))
    return bool(reserved)


def process_ads(ads):
    for ad in ads:
        ad_id = str(ad.get("id"))
        if not ad_id or not is_new(ad_id):
            continue

        price = _ad_price(ad)
        if price < MIN_PRICE or price > MAX_PRICE:
            logger.debug("Anuncio %s fuera de rango de precio (%.2f €).", ad_id, price)
            continue

        if SKIP_RESERVED and _is_reserved(ad):
            logger.debug("Anuncio %s reservado.", ad_id)
            continue

        coords = _ad_coords(ad)
        if coords is None:
            logger.debug("Anuncio %s sin coordenadas.", ad_id)
            continue

        distance_km = distance_to_motril(*coords)
        if distance_km > RADIUS_KM:
            logger.debug(
                "Anuncio %s a %.1f km de Motril, fuera del radio de %d km.",
                ad_id,
                distance_km,
                RADIUS_KM,
            )
            continue

        age_minutes = _ad_age_minutes(ad)
        condition = ad.get("condition", "")
        score, benefit, _ = compute_score(distance_km, price, condition, age_minutes)

        if score < MIN_SCORE_TO_NOTIFY:
            logger.debug(
                "Anuncio %s con puntuación %.0f por debajo del umbral (%d).",
                ad_id,
                score,
                MIN_SCORE_TO_NOTIFY,
            )
            continue

        message = build_message(
            title=ad.get("title", "Sin título"),
            price=price,
            city=_ad_city(ad),
            distance_km=distance_km,
            age_minutes=age_minutes,
            benefit=benefit,
            score=score,
            url=_ad_url(ad),
        )
        ok = send_telegram(message)
        logger.info(
            "Notificación %s | %s | %.2f € | %.1f km | pun. %.0f",
            "ENVIADA" if ok else "FALLIDA (se reintentará)",
            ad.get("title", ""),
            price,
            distance_km,
            score,
        )
        if ok:
            mark_seen(ad_id)


def scan_keywords(client, max_results, scan_type="rápida"):
    for keyword in SEARCH_KEYWORDS:
        try:
            ads = client.search(keyword, max_results=max_results)
            logger.info("Búsqueda %s '%s': %d anuncios.", scan_type, keyword, len(ads))
            process_ads(ads)
        except Exception as exc:
            logger.exception("Error procesando '%s': %s", keyword, exc)
        time.sleep(1)


def run_cycle(client, last_deep):
    cycle_start = time.time()
    scan_keywords(client, MAX_RESULTS)
    if time.time() - last_deep >= DEEP_SCAN_INTERVAL:
        scan_keywords(client, DEEP_SCAN_RESULTS, scan_type="profunda")
        last_deep = time.time()
    return time.time() - cycle_start, last_deep


def main():
    parser = argparse.ArgumentParser(description="Bot de alertas de Wallapop en Motril")
    parser.add_argument(
        "--once",
        action="store_true",
        help="ejecuta una única comprobación y sale (modo GitHub Actions)",
    )
    args = parser.parse_args()

    client = WallapopClient()
    logger.info("Bot Wallapop iniciado. Ciudad: Motril, radio %d km.", RADIUS_KM)
    logger.info(
        "Comprobación rápida cada %d s. Escaneo profundo cada %d s (%d anuncios/palabra).",
        CHECK_INTERVAL,
        DEEP_SCAN_INTERVAL,
        DEEP_SCAN_RESULTS,
    )

    if args.once:
        logger.info("Modo única: ejecutando una comprobación...")
        run_cycle(client, 0)
        logger.info("Ejecución única finalizada.")
        return

    last_deep = 0
    while True:
        elapsed, last_deep = run_cycle(client, last_deep)
        sleep_for = max(1, CHECK_INTERVAL - elapsed)
        logger.info("Siguiente comprobación en %.0f s...", sleep_for)
        time.sleep(sleep_for)


if __name__ == "__main__":
    main()
