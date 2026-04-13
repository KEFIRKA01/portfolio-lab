from __future__ import annotations

from dataclasses import dataclass
from statistics import mean
from typing import Iterable, List

from .domain import Item, chance_score, effort_hours, lane, risk_score, value_score

@dataclass(slots=True)
class Opportunity:
    item_id: str
    lane: str
    risk: int
    value: int
    chance: int
    effort: float
    stability: int
    fit: int
    recommendation: str

def stability_index(item: Item) -> int:
    score = 78 - len(item.signals) * 4 - (8 if item.status == "blocked" else 0) - (5 if item.assigned_to is None else 0)
    score += 4 if item.status in {"approved", "confirmed", "scheduled", "assigned"} else 0
    return max(15, min(score, 99))

def fit_index(item: Item) -> int:
    score = 20 + (15 if item.budget >= 20000 else 8) + (18 if chance_score(item) >= 70 else 10)
    score += 16 if lane(item) in {"priority", "critical"} else 8
    score += min(len(item.notes) * 2, 10)
    return min(score, 100)

def economics(item: Item) -> float:
    multiplier = 1.0 + (0.35 if item.budget >= 50000 else 0.1) + (0.2 if "vip" in item.category else 0.0)
    return round(item.budget * multiplier, 2)

def card(item: Item) -> Opportunity:
    current_lane = lane(item)
    stability = stability_index(item)
    chance = chance_score(item)
    recommendation = "взять первым" if current_lane == "critical" else ("вести быстро" if chance >= 70 else "держать в основном потоке")
    return Opportunity(item.item_id, current_lane, risk_score(item), value_score(item), chance, effort_hours(item), stability, fit_index(item), recommendation)

def digest(items: Iterable[Item]) -> dict:
    rows = list(items)
    if not rows:
        return {"avg_risk": 0, "avg_value": 0, "avg_chance": 0, "avg_stability": 0, "avg_fit": 0}
    return {
        "avg_risk": round(mean(risk_score(item) for item in rows), 1),
        "avg_value": round(mean(value_score(item) for item in rows), 1),
        "avg_chance": round(mean(chance_score(item) for item in rows), 1),
        "avg_stability": round(mean(stability_index(item) for item in rows), 1),
        "avg_fit": round(mean(fit_index(item) for item in rows), 1),
    }
