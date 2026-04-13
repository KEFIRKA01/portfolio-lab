from __future__ import annotations

from dataclasses import dataclass
from typing import List

from .domain import CATEGORIES, RISKS, Item, chance_score, display_label, lane, risk_score

@dataclass(slots=True)
class PolicyDecision:
    owner: str
    requires_manual_review: bool
    blockers: List[str]
    sla_minutes: int
    escalation_label: str

def owner_route(item: Item) -> str:
    if item.category in CATEGORIES[:2]:
        return "priority_operator"
    if "vip" in item.category:
        return "owner"
    return "standard_operator"

def blockers(item: Item) -> List[str]:
    rows: List[str] = []
    if item.assigned_to is None:
        rows.append("нет ответственного")
    if item.status == "blocked":
        rows.append("статус блокировки")
    if len(item.signals) >= 3:
        rows.append("слишком много риск-сигналов")
    if chance_score(item) < 45:
        rows.append("низкий шанс успешного прохода")
    return rows

def manual_review(item: Item) -> bool:
    return risk_score(item) >= 65 or "vip" in item.category or item.budget >= 50000

def sla_minutes(item: Item) -> int:
    if lane(item) == "critical":
        return 15
    if lane(item) == "priority":
        return 45
    return 180

def decision(item: Item) -> PolicyDecision:
    rows = blockers(item)
    return PolicyDecision(
        owner=owner_route(item),
        requires_manual_review=manual_review(item),
        blockers=rows,
        sla_minutes=sla_minutes(item),
        escalation_label=display_label(RISKS[len(item.signals) % len(RISKS)]) if RISKS else "стандартный",
    )
