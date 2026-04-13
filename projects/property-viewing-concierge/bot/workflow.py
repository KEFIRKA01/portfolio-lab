from __future__ import annotations

from dataclasses import dataclass
from typing import List

from .domain import CATEGORIES, FEATURES, RISKS, Item, lane

@dataclass(slots=True)
class Playbook:
    stage: str
    owner: str
    checks: List[str]
    escalation_rule: str

def build_playbook(item: Item) -> List[Playbook]:
    checks = ["Уточнить контекст", "Проверить текущий статус", "Собрать недостающие данные"]
    if item.category in CATEGORIES[:2]:
        checks.append("Проверить ускоренный маршрут")
    if lane(item) == "critical":
        checks.append("Поднять ручное сопровождение")
    return [
        Playbook(stage="intake", owner="coordinator", checks=checks, escalation_rule=RISKS[0]),
        Playbook(stage="execution", owner="operator", checks=["Держать SLA", "Сверить передачу"], escalation_rule=RISKS[1]),
        Playbook(stage="review", owner="owner", checks=["Закрыть результат", "Снять последующее сопровождение"], escalation_rule=RISKS[-1]),
    ]

def handoff_targets(item: Item) -> List[str]:
    targets = ["operator", "owner"]
    if item.category in CATEGORIES[-2:]:
        targets.append("specialist")
    if len(item.signals) >= 2:
        targets.append("escalation")
    return targets

def escalation_reason(item: Item) -> str | None:
    if lane(item) == "critical":
        return f"критическая очередь / {item.category}"
    if item.status == "blocked":
        return "статус блокировки"
    if len(item.signals) >= 3:
        return "накопилось слишком много риск-сигналов"
    return None

def workflow_note(item: Item) -> str:
    feature = FEATURES[len(item.tags) % len(FEATURES)] if FEATURES else "сценарий"
    return f"{feature}: передача -> {', '.join(handoff_targets(item))}"
