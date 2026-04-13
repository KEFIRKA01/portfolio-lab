from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Dict, List


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


ALLOWED_TRANSITIONS = {
    "new": {"qualified", "rejected"},
    "qualified": {"in_progress", "rejected"},
    "in_progress": {"waiting_customer", "done"},
    "waiting_customer": {"in_progress", "done"},
    "done": set(),
    "rejected": set(),
}


@dataclass(slots=True)
class TimelineEntry:
    kind: str
    note: str
    created_at: datetime = field(default_factory=utc_now)


@dataclass(slots=True)
class ServiceRequest:
    request_id: str
    customer_name: str
    summary: str
    status: str = "new"
    created_at: datetime = field(default_factory=utc_now)
    priority: str = "normal"
    timeline: List[TimelineEntry] = field(default_factory=list)

    def as_dict(self) -> Dict[str, object]:
        payload = asdict(self)
        payload["created_at"] = self.created_at.isoformat()
        payload["timeline"] = [
            {"kind": entry.kind, "note": entry.note, "created_at": entry.created_at.isoformat()} for entry in self.timeline
        ]
        payload["flow_type"] = infer_flow_type(self.summary)
        payload["suggested_reply"] = suggest_reply(self)
        return payload


def can_transition(current_status: str, next_status: str) -> bool:
    return next_status in ALLOWED_TRANSITIONS.get(current_status, set())


def reminder_due(created_at: datetime, hours: int = 12) -> datetime:
    return created_at + timedelta(hours=hours)


def manager_alert_text(request: ServiceRequest) -> str:
    return (
        f"Новая заявка #{request.request_id}\n"
        f"Клиент: {request.customer_name}\n"
        f"Суть: {request.summary}\n"
        f"Статус: {request.status}\n"
        f"Приоритет: {request.priority}\n"
        f"Тип потока: {infer_flow_type(request.summary)}"
    )


def next_actions(status: str) -> List[str]:
    actions = {
        "new": ["уточнить задачу", "оценить срочность"],
        "qualified": ["подготовить предложение", "согласовать этапы"],
        "in_progress": ["обновить статус", "зафиксировать блокеры"],
        "waiting_customer": ["отправить напоминание"],
        "done": ["запросить отзыв"],
        "rejected": ["закрыть карточку"],
    }
    return actions.get(status, [])


def infer_priority(summary: str) -> str:
    lowered = summary.lower()
    if "срочно" in lowered or "urgent" in lowered:
        return "high"
    if "бот" in lowered or "интегра" in lowered or "white-label" in lowered:
        return "medium"
    return "normal"


def infer_flow_type(summary: str) -> str:
    lowered = summary.lower()
    if "запись" in lowered or "бронь" in lowered:
        return "booking"
    if "поддерж" in lowered or "тикет" in lowered:
        return "support"
    if "white-label" in lowered or "white label" in lowered:
        return "partner_portal"
    if "доставка" in lowered or "логист" in lowered:
        return "operations"
    return "sales"


def required_inputs(flow_type: str) -> List[str]:
    requirements = {
        "sales": ["имя", "контакт", "описание задачи"],
        "booking": ["дата", "время", "контакт"],
        "support": ["проблема", "скриншот", "контакт"],
        "partner_portal": ["бренд", "доступы", "сценарий white-label"],
        "operations": ["маршрут", "дедлайн", "контакт менеджера"],
    }
    return requirements.get(flow_type, ["контакт", "описание"])


def suggest_reply(request: ServiceRequest) -> str:
    flow_type = infer_flow_type(request.summary)
    inputs = ", ".join(required_inputs(flow_type))
    return f"Принял задачу по сценарию {flow_type}. Чтобы быстро перейти к реализации, полезно уточнить: {inputs}."


class RequestBoard:
    def __init__(self) -> None:
        self._items: Dict[str, ServiceRequest] = {}

    def add(self, request: ServiceRequest) -> None:
        if not request.priority or request.priority == "normal":
            request.priority = infer_priority(request.summary)
        request.timeline.append(TimelineEntry(kind="created", note="Заявка создана"))
        self._items[request.request_id] = request

    def get(self, request_id: str) -> ServiceRequest:
        return self._items[request_id]

    def transition(self, request_id: str, next_status: str, note: str) -> None:
        request = self._items[request_id]
        if not can_transition(request.status, next_status):
            raise ValueError(f"Cannot move {request.status} -> {next_status}")
        request.status = next_status
        request.timeline.append(TimelineEntry(kind="status", note=note))

    def reminder_candidates(self, now: datetime) -> List[ServiceRequest]:
        return [
            request
            for request in self._items.values()
            if request.status == "waiting_customer" and reminder_due(request.created_at) <= now
        ]

    def digest(self) -> Dict[str, int]:
        stats = {"total": len(self._items), "high_priority": 0, "waiting_customer": 0, "partner_portal": 0}
        for request in self._items.values():
            if request.priority == "high":
                stats["high_priority"] += 1
            if request.status == "waiting_customer":
                stats["waiting_customer"] += 1
            if infer_flow_type(request.summary) == "partner_portal":
                stats["partner_portal"] += 1
        return stats
