from __future__ import annotations

from dataclasses import dataclass

@dataclass(slots=True)
class Widget:
    widget_id: str
    title: str
    kind: str
    description: str

def widgets() -> list[Widget]:
        return [
            Widget("queue", "Главная очередь", "table", "Приоритеты и SLA"),
            Widget("risk", "Риск-панель", "scoreboard", "Критичные сигналы и ручная проверка"),
            Widget("economics", "Экономика", "metric", "Взвешенная экономика и соответствие"),
            Widget("timeline", "Таймлайн", "feed", "История событий по объектам"),
            Widget("ops", "Операторский блок", "summary", "Сводка по передаче и блокерам"),
        ]

def default_filters() -> list[str]:
    return ["all", "critical", "priority", "execution", "unassigned", "manual-review"]
