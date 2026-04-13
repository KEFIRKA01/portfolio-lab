from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from typing import Iterable, List

from .analytics import card
from .domain import Item, utc_now

@dataclass(slots=True)
class SimulationFrame:
    item_id: str
    projected_status: str
    projected_delay_hours: int
    recommendation: str

def project(items: Iterable[Item]) -> List[SimulationFrame]:
    rows: List[SimulationFrame] = []
    for item in items:
        view = card(item)
        delay = 0 if view.chance >= 70 else 6
        rows.append(SimulationFrame(
            item_id=item.item_id,
            projected_status="resolved" if view.chance >= 75 else "in_progress",
            projected_delay_hours=delay,
            recommendation=view.recommendation,
        ))
    return rows

def synthetic_item(seed_id: str, category: str) -> Item:
    return Item(
        item_id=seed_id,
        customer_name="Тестовый пользователь",
        title="Тестовый сценарий",
        category=category,
        priority=58,
        budget=21000,
        deadline_at=utc_now() + timedelta(hours=5),
        tags=[category, "симуляция"],
        signals=["смоделировано"],
        notes=["создано симуляцией"],
    )

def load_test_batch(categories: list[str]) -> List[Item]:
    return [synthetic_item(f"sim-{idx}", category) for idx, category in enumerate(categories, start=1)]
