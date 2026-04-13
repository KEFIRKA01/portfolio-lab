from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from statistics import mean
from typing import Any, Dict, Iterable, List

TITLE = "Магазин в Telegram Orbit"
ENTITY = "заказ"
OPERATOR = "оператор магазина"
METRIC = "средний чек и повторные заказы"
DISPLAY_MAP = {
    "customer": "клиент",
    "operator": "оператор",
    "warehouse": "склад",
    "owner": "владелец",
    "user": "пользователь",
    "security": "безопасность",
    "admin": "администратор",
    "patient": "пациент",
    "coordinator": "координатор",
    "doctor": "врач",
    "client": "клиент",
    "agent": "агент",
    "broker": "брокер",
    "guest": "гость",
    "scanner": "сканер доступа",
    "student": "студент",
    "mentor": "ментор",
    "recruiter": "рекрутер",
    "manager": "менеджер",
    "requester": "инициатор",
    "controller": "контролер",
    "approver": "согласующий",
    "driver": "водитель",
    "dispatcher": "диспетчер",
    "mechanic": "механик",
    "host": "хостес",
    "supervisor": "супервайзер",
    "lawyer": "юрист",
    "member": "участник",
    "retention": "менеджер удержания",
    "billing": "биллинг",
    "technician": "инженер",
    "partner": "партнер",
    "legal": "юридический отдел",
    "specialist": "специалист",
    "escalation": "эскалация",
    "electronics": "электроника",
    "fashion": "одежда и стиль",
    "home": "товары для дома",
    "gifts": "подарки",
    "subscription": "подписка",
    "admin-panel": "админ-панель",
    "partner-portal": "партнерский портал",
    "vpn": "VPN",
    "crm": "CRM",
    "finance": "финансы",
    "therapist": "терапевт",
    "dentist": "стоматолог",
    "checkup": "чекап",
    "tests": "анализы",
    "followup": "повторный визит",
    "rent": "аренда",
    "sale": "продажа",
    "commercial": "коммерческая недвижимость",
    "newbuilding": "новостройка",
    "mortgage": "ипотека",
    "conference": "конференция",
    "concert": "концерт",
    "meetup": "митап",
    "vip": "VIP",
    "stream": "онлайн-трансляция",
    "onboarding": "онбординг",
    "homework": "домашняя работа",
    "office-hours": "часы с ментором",
    "certificate": "сертификат",
    "support": "поддержка",
    "frontend": "frontend",
    "backend": "backend",
    "qa": "тестирование",
    "product": "product",
    "opex": "операционные расходы",
    "marketing": "маркетинг",
    "software": "софт",
    "travel": "командировки",
    "urgent": "срочно",
    "delivery": "доставка",
    "pickup": "забор",
    "maintenance": "обслуживание",
    "incident": "инцидент",
    "dinner": "ужин",
    "birthday": "день рождения",
    "corporate": "корпоратив",
    "terrace": "терраса",
    "carrier": "перевозчик",
    "stock-hold": "резерв остатков",
    "vip-client": "VIP клиент",
    "crossdock": "кросс-докинг",
    "contract": "договор",
    "employment": "трудовое право",
    "ip": "интеллектуальная собственность",
    "dispute": "спор",
    "renewal": "продление",
    "downgrade": "снижение тарифа",
    "failed-payment": "неудачный платеж",
    "pause": "пауза",
    "installation": "установка",
    "repair": "ремонт",
    "inspection": "осмотр",
    "parts": "запчасти",
    "marketplace": "маркетплейс",
    "reseller": "реселлер",
    "affiliate": "партнерская программа",
    "integration": "интеграция",
    "enterprise": "корпоративный",
    "new": "новый",
    "in_progress": "в работе",
    "assigned": "назначен",
    "blocked": "заблокирован",
    "resolved": "решён",
    "escalated": "эскалирован",
    "approved": "согласован",
    "confirmed": "подтверждён",
    "scheduled": "запланирован",
    "archived": "архивирован",
    "critical": "критический",
    "priority": "приоритетный",
    "execution": "исполнение",
    "standard": "стандартный",
    "priority_operator": "приоритетный оператор",
    "standard_operator": "основной оператор"
}
CATEGORIES = [
    "electronics",
    "fashion",
    "home",
    "gifts",
    "subscription"
]
SCENARIOS = [
    "Быстрый заказ",
    "Повторная покупка",
    "Подарочный набор",
    "Дополнительная продажа",
    "Доставка сегодня"
]
FEATURES = [
    "каталог с подборками",
    "корзина и сегментация клиента",
    "управление доставкой",
    "операторская очередь",
    "сигналы по брошенным корзинам"
]
RISKS = [
    "высокий чек",
    "новый покупатель",
    "срочная доставка",
    "мало остатка",
    "жалоба на прошлый заказ"
]

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

def display_label(value: str) -> str:
    return DISPLAY_MAP.get(value, value)

@dataclass(slots=True)
class Actor:
    actor_id: str
    name: str
    role: str
    segment: str
    trust: int = 50
    flags: List[str] = field(default_factory=list)

@dataclass(slots=True)
class Event:
    at: datetime
    action: str
    author: str
    payload: str

@dataclass(slots=True)
class Item:
    item_id: str
    customer_name: str
    title: str
    category: str
    status: str = "new"
    priority: int = 40
    budget: int = 0
    deadline_at: datetime = field(default_factory=lambda: utc_now() + timedelta(hours=8))
    assigned_to: str | None = None
    tags: List[str] = field(default_factory=list)
    signals: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    history: List[Event] = field(default_factory=list)

    def add_event(self, action: str, author: str, payload: str) -> None:
        self.history.append(Event(at=utc_now(), action=action, author=author, payload=payload))

    def add_note(self, note: str, author: str = "system") -> None:
        self.notes.append(note)
        self.add_event("note", author, note)

    def add_signal(self, signal: str, author: str = "system") -> None:
        if signal not in self.signals:
            self.signals.append(signal)
        self.add_event("signal", author, signal)

@dataclass(slots=True)
class Blueprint:
    name: str
    category: str
    feature: str
    risk: str
    lane: str

def blueprints() -> List[Blueprint]:
    rows: List[Blueprint] = []
    for idx, name in enumerate(SCENARIOS):
        rows.append(Blueprint(
            name=name,
            category=CATEGORIES[idx % len(CATEGORIES)],
            feature=FEATURES[idx % len(FEATURES)],
            risk=RISKS[idx % len(RISKS)],
            lane="priority" if idx % 2 else "standard",
        ))
    return rows

def normalize_tags(values: Iterable[str]) -> List[str]:
    output: List[str] = []
    for value in values:
        token = value.strip().lower().replace(" ", "-")
        if token and token not in output:
            output.append(token)
    return output

def risk_score(item: Item) -> int:
    score = item.priority // 2 + len(item.signals) * 7 + len(item.notes) * 2
    score += 12 if item.deadline_at <= utc_now() + timedelta(hours=4) else 0
    score += 10 if item.budget >= 50000 else 0
    score += 8 if item.status in {"blocked", "escalated"} else 0
    score += 5 if item.assigned_to is None else 0
    return min(score, 100)

def value_score(item: Item) -> int:
    score = 8 + item.budget // 2500
    score += 6 if item.category in CATEGORIES[:2] else 3
    score += 4 if item.status in {"approved", "confirmed", "scheduled", "assigned"} else 0
    return min(score, 100)

def chance_score(item: Item) -> int:
    score = 54 + (8 if item.assigned_to else -3) + (10 if item.status in {"in_progress", "assigned", "approved"} else 0)
    score += max(0, 10 - len(item.signals) * 2)
    score -= 6 if item.status == "blocked" else 0
    return max(5, min(score, 95))

def effort_hours(item: Item) -> float:
    base = 2.0 + len(item.tags) * 0.25 + len(item.signals) * 0.45
    base += 1.5 if item.budget >= 50000 else 0.5
    return round(base, 1)

def lane(item: Item) -> str:
    risk = risk_score(item)
    value = value_score(item)
    if risk >= 70 and value >= 20:
        return "critical"
    if risk >= 55 or value >= 25:
        return "priority"
    if item.status in {"approved", "confirmed", "scheduled"}:
        return "execution"
    return "standard"

def due_bucket(item: Item, now: datetime | None = None) -> str:
    now = now or utc_now()
    hours = (item.deadline_at - now).total_seconds() / 3600
    if hours <= 2:
        return "now"
    if hours <= 8:
        return "today"
    if hours <= 24:
        return "next"
    return "later"

def checklist(item: Item) -> List[str]:
    rows = [
        "Проверить данные по объекту",
        "Сверить сигналы риска",
        "Оценить назначение ответственного",
    ]
    if item.category in CATEGORIES[:2]:
        rows.append("Проверить приоритетный маршрут обработки")
    if item.budget >= 40000:
        rows.append("Согласовать сценарий с повышенной ценностью")
    if due_bucket(item) == "now":
        rows.append("Поднять срочный флаг в ручной очереди")
    return rows

def next_action(item: Item) -> str:
    if lane(item) == "critical":
        return "Срочно передать в ручную обработку и держать под усиленным контролем."
    if lane(item) == "priority":
        return "Поставить в приоритетную очередь и уточнить недостающие данные."
    if item.status in {"approved", "confirmed", "scheduled"}:
        return "Перевести в основной контур исполнения и мониторить SLA."
    return "Оставить в основном потоке и ждать следующего шага."

def summary(items: Iterable[Item]) -> Dict[str, Any]:
    rows = list(items)
    if not rows:
        return {"total": 0, "avg_risk": 0, "avg_value": 0, "avg_chance": 0}
    return {
        "total": len(rows),
        "avg_risk": round(mean(risk_score(item) for item in rows), 1),
        "avg_value": round(mean(value_score(item) for item in rows), 1),
        "avg_chance": round(mean(chance_score(item) for item in rows), 1),
        "critical": sum(1 for item in rows if lane(item) == "critical"),
        "execution": sum(1 for item in rows if lane(item) == "execution"),
    }

def snapshot(item: Item) -> Dict[str, Any]:
    data = asdict(item)
    data["deadline_at"] = item.deadline_at.isoformat()
    data["risk_score"] = risk_score(item)
    data["value_score"] = value_score(item)
    data["chance_score"] = chance_score(item)
    data["effort_hours"] = effort_hours(item)
    data["lane"] = display_label(lane(item))
    data["next_action"] = next_action(item)
    data["checklist"] = checklist(item)
    return data
