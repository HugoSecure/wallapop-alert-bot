from config import (
    CONDITION_SCORES,
    FRESHNESS_WINDOW_MINUTES,
    MAX_EXPECTED_BENEFIT,
    MAX_PRICE,
    RADIUS_KM,
    RESALE_MULTIPLIER,
    SCORE_WEIGHTS,
)


def estimated_benefit(price):
    return price * (RESALE_MULTIPLIER - 1)


def _norm(value, ref_max, invert=False):
    if ref_max <= 0:
        return 100.0
    score = max(0.0, min(100.0, 100.0 * value / ref_max))
    return 100.0 - score if invert else score


def score_distance(distance_km):
    if RADIUS_KM <= 0:
        return 0.0
    return max(0.0, 100.0 * (1.0 - distance_km / RADIUS_KM))


def score_price(price):
    return _norm(price, MAX_PRICE, invert=True)


def score_profit(benefit):
    return _norm(benefit, MAX_EXPECTED_BENEFIT)


def score_freshness(age_minutes):
    return max(0.0, 100.0 * (1.0 - age_minutes / FRESHNESS_WINDOW_MINUTES))


def score_condition(item_condition):
    return CONDITION_SCORES.get(item_condition, 50)


def compute_score(distance_km, price, item_condition, age_minutes):
    benefit = estimated_benefit(price)
    scores = {
        "distance": score_distance(distance_km),
        "price": score_price(price),
        "profit": score_profit(benefit),
        "freshness": score_freshness(age_minutes),
        "condition": score_condition(item_condition),
    }
    total_weight = sum(SCORE_WEIGHTS.values()) or 1
    final = sum(scores[k] * SCORE_WEIGHTS[k] for k in scores) / total_weight
    return final, benefit, scores
