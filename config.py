import os

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

# ---------- Ubicación (criterio MÁS importante) ----------
CITY = "Motril"
RADIUS_KM = 5

# Coordenadas del centro de Motril (Granada, España)
LATITUDE = 36.7444
LONGITUDE = -3.5208

# ---------- Productos a buscar (cámbialos por los que quieras revender) ----------
SEARCH_KEYWORDS = [
    "iphone",
    "playstation",
    "nintendo switch",
    "ps4",
    "ps5",
]

# ---------- Búsqueda ----------
MIN_PRICE = 0
MAX_PRICE = 500
MAX_RESULTS = 100  # anuncios a revisar por palabra en cada comprobación rápida
SKIP_RESERVED = True  # no notificar anuncios reservados

# Escaneo profundo: revisa más anuncios por palabra para no perder anuncios de
# Motril que caen fuera de los más recientes a nivel nacional
DEEP_SCAN_INTERVAL = 300  # segundos entre escaneos profundos
DEEP_SCAN_RESULTS = 500  # anuncios a revisar por palabra en el escaneo profundo

# ---------- Temporización ----------
CHECK_INTERVAL = 20  # segundos entre comprobaciones completas

# ---------- Estimación de beneficio ----------
RESALE_MULTIPLIER = 1.5  # ejemplo: compras a 100 € y revendes a 150 €

# ---------- Puntuación ----------
# Prioridad: 1. Distancia, 2. Precio, 3. Beneficio, 4. Tiempo, 5. Estado
SCORE_WEIGHTS = {
    "distance": 40,
    "price": 20,
    "profit": 20,
    "freshness": 15,
    "condition": 5,
}
MAX_EXPECTED_BENEFIT = 100  # beneficio de referencia para normalizar la puntuación
FRESHNESS_WINDOW_MINUTES = 6 * 60  # ventana en la que un anuncio se considera "fresco"
MIN_SCORE_TO_NOTIFY = 50  # si pones 0, avisa de todo lo que esté dentro del radio

CONDITION_SCORES = {
    "new": 100,
    "like_new": 90,
    "almost_new": 90,
    "reconditioned": 70,
    "good": 60,
    "regular": 40,
    "fair": 40,
    "poor": 20,
    "for_parts": 10,
}

# ---------- Telegram ----------
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# ---------- HTTP ----------
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
REQUEST_TIMEOUT = 15
