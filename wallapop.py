import logging
import time

import requests

from config import (
    LATITUDE,
    LONGITUDE,
    MAX_RESULTS,
    REQUEST_TIMEOUT,
    USER_AGENT,
)

logger = logging.getLogger(__name__)

COMPONENTS_URL = "https://api.wallapop.com/api/v3/search/components"
SECTION_URL = "https://api.wallapop.com/api/v3/search/section"

DEFAULT_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": USER_AGENT,
    "X-DeviceOS": "0",
    "Origin": "https://es.wallapop.com",
    "Referer": "https://es.wallapop.com/",
}


class WallapopClient:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)

    def _get(self, url, params):
        resp = None
        for attempt in range(3):
            try:
                resp = self.session.get(url, params=params, timeout=REQUEST_TIMEOUT)
                resp.raise_for_status()
                return resp.json()
            except requests.HTTPError as exc:
                if resp.status_code == 429:
                    wait = 5 * (2**attempt)
                    logger.warning("Límite de peticiones (429). Esperando %d s...", wait)
                    time.sleep(wait)
                else:
                    logger.warning(
                        "Error HTTP %s en %s (intento %d/3): %s",
                        resp.status_code,
                        url,
                        attempt + 1,
                        exc,
                    )
                    time.sleep(2 * (attempt + 1))
            except Exception as exc:
                logger.warning("Error en %s (intento %d/3): %s", url, attempt + 1, exc)
                time.sleep(2 * (attempt + 1))
        return None

    def _search_id(self, keyword):
        body = self._get(
            COMPONENTS_URL,
            {
                "keywords": keyword,
                "source": "search_box",
                "latitude": str(LATITUDE),
                "longitude": str(LONGITUDE),
            },
        )
        if not body:
            return None
        for component in body.get("components", []):
            if component.get("type") == "search_results":
                query_params = (component.get("type_data") or {}).get("query_params") or {}
                return query_params.get("search_id")
        return None

    def search(self, keyword, max_results=MAX_RESULTS):
        search_id = self._search_id(keyword)
        if not search_id:
            logger.warning("No se pudo obtener search_id para '%s'.", keyword)
            return []

        items = []
        next_page = None
        while len(items) < max_results:
            params = {
                "keywords": keyword,
                "search_id": search_id,
                "latitude": str(LATITUDE),
                "longitude": str(LONGITUDE),
                "section_type": "organic_search_results",
                "source": "deep_link",
                "order_by": "newest",
            }
            if next_page:
                params["next_page"] = next_page

            body = self._get(SECTION_URL, params)
            if not body:
                break
            data = body.get("data") or {}
            page_items = (data.get("section") or {}).get("items") or []
            items.extend(page_items)
            next_page = (body.get("meta") or {}).get("next_page")
            if not next_page or not page_items:
                break
            if len(items) < max_results:
                time.sleep(0.6)

        return items[:max_results]
