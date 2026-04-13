from __future__ import annotations

from datetime import timedelta

from .domain import CATEGORIES, Item, utc_now

def synthetic_batch(size: int = 8) -> list[Item]:
    rows: list[Item] = []
    for idx in range(1, size + 1):
        category = CATEGORIES[(idx - 1) % len(CATEGORIES)]
        rows.append(
            Item(
                item_id=f"fixture-{idx}",
                customer_name=f"Тестовый пользователь {idx}",
                title=f"Демо-сценарий {idx}",
                category=category,
                priority=30 + idx * 7,
                budget=10000 + idx * 4200,
                deadline_at=utc_now() + timedelta(hours=idx),
                tags=[category, "демо-набор"],
                signals=["демо-сигнал"] if idx % 2 else [],
                notes=["создано тестовым генератором"],
            )
        )
    return rows

def status_matrix() -> dict[str, list[str]]:
    return {
        "new": ["assign", "note", "escalate"],
        "assigned": ["progress", "postpone", "resolve"],
        "blocked": ["manual_review", "collect_data", "escalate"],
        "resolved": ["archive", "reopen"],
    }
