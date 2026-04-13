from __future__ import annotations

from typing import Iterable

from .analytics import card, digest, economics
from .policies import decision
from .domain import METRIC, Item, display_label

def top_lines(items: Iterable[Item]) -> list[str]:
    rows = sorted((card(item) for item in items), key=lambda row: (row.chance, row.value), reverse=True)
    return [
        f"{row.item_id} | очередь={display_label(row.lane)} | шанс={row.chance} | ценность={row.value} | время={row.effort} ч"
        for row in rows[:5]
    ]

def owner_report(items: Iterable[Item]) -> str:
    rows = list(items)
    stats = digest(rows)
    lines = [
        f"Главная метрика: {METRIC}",
        f"Средний шанс: {stats['avg_chance']}",
        f"Средняя ценность: {stats['avg_value']}",
        f"Средняя стабильность: {stats['avg_stability']}",
        f"Среднее соответствие: {stats['avg_fit']}",
        "Верхняя часть очереди:",
    ]
    lines.extend(top_lines(rows))
    manual = sum(1 for item in rows if decision(item).requires_manual_review)
    lines.append(f"Ручная проверка: {manual}")
    return "\n".join(lines)

def economics_report(items: Iterable[Item]) -> str:
    total = sum(economics(item) for item in items)
    return f"Оценка взвешенной экономики: {round(total, 2)}"
