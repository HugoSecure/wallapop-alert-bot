import math

from config import LATITUDE, LONGITUDE, RADIUS_KM

_EARTH_RADIUS_KM = 6371.0


def haversine_km(lat1, lon1, lat2, lon2):
    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return _EARTH_RADIUS_KM * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def distance_to_motril(lat, lon):
    return haversine_km(LATITUDE, LONGITUDE, lat, lon)


def is_within_radius(lat, lon, radius_km=RADIUS_KM):
    return distance_to_motril(lat, lon) <= radius_km
