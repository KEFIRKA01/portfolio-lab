from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from typing import Any, Dict, List


STATUS_TRANSITIONS = {
    "new": {"qualified", "rejected"},
    "qualified": {"proposal_sent", "in_progress", "rejected"},
    "proposal_sent": {"won", "lost", "in_progress"},
    "in_progress": {"won", "lost"},
    "won": set(),
    "lost": set(),
    "rejected": set(),
}


@dataclass(slots=True)
class RoutingRule:
    name: str
    destination: str
    required_tags: List[str] = field(default_factory=list)
    channels: List[str] = field(default_factory=list)
    min_budget: int = 0
    priority_boost: int = 0


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def normalize_phone(phone: str) -> str:
    digits = "".join(char for char in phone if char.isdigit())
    if digits.startswith("8") and len(digits) == 11:
        digits = "7" + digits[1:]
    return digits


def normalize_text(value: str) -> str:
    return " ".join(value.strip().lower().split())


def build_signature(name: str, phone: str, source: str) -> str:
    raw = "|".join(part.strip().lower() for part in (name, normalize_phone(phone), source))
    return sha256(raw.encode("utf-8")).hexdigest()[:16]


def classify_channel(source: str) -> str:
    lowered = source.lower()
    if "telegram" in lowered:
        return "telegram"
    if "landing" in lowered or "site" in lowered:
        return "site"
    if "ads" in lowered or "direct" in lowered:
        return "paid"
    return "manual"


def lead_temperature(budget: int | None, source: str) -> str:
    if budget and budget >= 150_000:
        return "hot"
    if "telegram" in source.lower() or (budget and budget >= 70_000):
        return "warm"
    return "cold"


def infer_tags(source: str, budget: int | None, note: str | None = None) -> List[str]:
    tags: List[str] = []
    lowered_source = source.lower()
    lowered_note = normalize_text(note or "")
    if "telegram" in lowered_source:
        tags.append("telegram")
    if "landing" in lowered_source:
        tags.append("landing")
    if "crm" in lowered_note or "amo" in lowered_note or "bitrix" in lowered_note:
        tags.append("crm")
    if "api" in lowered_note or "webhook" in lowered_note:
        tags.append("api")
    if "срочно" in lowered_note or "urgent" in lowered_note:
        tags.append("urgent")
    if "enterprise" in lowered_note or "b2b" in lowered_note:
        tags.append("enterprise")
    if "white label" in lowered_note or "white-label" in lowered_note:
        tags.append("white_label")
    if budget and budget >= 150_000:
        tags.append("high_budget")
    return sorted(set(tags))


def priority_score(source: str, budget: int | None, tags: List[str]) -> int:
    score = 20
    channel = classify_channel(source)
    if channel == "telegram":
        score += 15
    if channel == "paid":
        score += 5
    if budget:
        score += min(40, budget // 10_000)
    if "crm" in tags or "api" in tags:
        score += 10
    if "urgent" in tags:
        score += 8
    if "enterprise" in tags:
        score += 6
    return min(score, 100)


def sla_bucket(created_at: datetime, priority: int, status: str, now: datetime | None = None) -> str:
    current_time = now or utc_now()
    age = current_time - created_at
    if status in {"won", "lost", "rejected"}:
        return "closed"
    if priority >= 70 and age > timedelta(hours=1):
        return "breach_risk"
    if priority >= 45 and age > timedelta(hours=6):
        return "attention"
    return "healthy"


def route_lead(lead: "Lead", rules: List[RoutingRule]) -> Dict[str, Any]:
    matched_rules: List[str] = []
    destination = "general_queue"
    bonus = 0
    lead_tags = set(lead.tags or infer_tags(lead.source, lead.budget, lead.note))
    channel = classify_channel(lead.source)

    for rule in rules:
        tags_ok = set(rule.required_tags).issubset(lead_tags)
        channel_ok = not rule.channels or channel in rule.channels
        budget_ok = (lead.budget or 0) >= rule.min_budget
        if tags_ok and channel_ok and budget_ok:
            matched_rules.append(rule.name)
            destination = rule.destination
            bonus = max(bonus, rule.priority_boost)

    return {
        "destination": destination,
        "matched_rules": matched_rules,
        "priority_with_boost": min(lead.priority + bonus, 100),
    }


@dataclass(slots=True)
class Lead:
    lead_id: str
    name: str
    phone: str
    source: str
    note: str | None = None
    budget: int | None = None
    status: str = "new"
    created_at: datetime = field(default_factory=utc_now)
    tags: List[str] = field(default_factory=list)

    @property
    def signature(self) -> str:
        return build_signature(self.name, self.phone, self.source)

    @property
    def temperature(self) -> str:
        return lead_temperature(self.budget, self.source)

    @property
    def priority(self) -> int:
        prepared_tags = self.tags or infer_tags(self.source, self.budget, self.note)
        return priority_score(self.source, self.budget, prepared_tags)

    def as_dict(self) -> Dict[str, Any]:
        payload = asdict(self)
        payload["created_at"] = self.created_at.isoformat()
        payload["signature"] = self.signature
        payload["temperature"] = self.temperature
        payload["priority"] = self.priority
        payload["tags"] = self.tags or infer_tags(self.source, self.budget, self.note)
        payload["sla_bucket"] = sla_bucket(self.created_at, self.priority, self.status)
        return payload


@dataclass(slots=True)
class Event:
    lead_id: str
    kind: str
    payload: Dict[str, str]
    created_at: datetime = field(default_factory=utc_now)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "lead_id": self.lead_id,
            "kind": self.kind,
            "payload": self.payload,
            "created_at": self.created_at.isoformat(),
        }


class LeadStore:
    def __init__(self) -> None:
        self._leads: Dict[str, Lead] = {}
        self._events: List[Event] = []
        self._by_signature: Dict[str, str] = {}

    def add_lead(self, lead: Lead) -> str:
        if not lead.tags:
            lead.tags = infer_tags(lead.source, lead.budget, lead.note)

        signature = lead.signature
        if signature in self._by_signature:
            existing_id = self._by_signature[signature]
            self._events.append(Event(lead_id=existing_id, kind="duplicate_detected", payload={"source": lead.source}))
            return existing_id

        self._leads[lead.lead_id] = lead
        self._by_signature[signature] = lead.lead_id
        self._events.append(
            Event(
                lead_id=lead.lead_id,
                kind="lead_created",
                payload={"channel": classify_channel(lead.source), "temperature": lead.temperature},
            )
        )
        return lead.lead_id

    def get(self, lead_id: str) -> Lead:
        return self._leads[lead_id]

    def update_status(self, lead_id: str, status: str) -> None:
        lead = self._leads[lead_id]
        if status not in STATUS_TRANSITIONS.get(lead.status, set()):
            raise ValueError(f"Cannot move {lead.status} -> {status}")
        lead.status = status
        self._events.append(Event(lead_id=lead_id, kind="status_changed", payload={"status": status}))

    def append_note(self, lead_id: str, note: str) -> None:
        lead = self._leads[lead_id]
        lead.note = note
        lead.tags = infer_tags(lead.source, lead.budget, note)
        self._events.append(Event(lead_id=lead_id, kind="note_updated", payload={"note": note[:80]}))

    def record_payment(self, lead_id: str, amount: int, gateway: str) -> None:
        self._events.append(
            Event(lead_id=lead_id, kind="payment_callback", payload={"amount": str(amount), "gateway": gateway})
        )

    def all_leads(self, status: str | None = None) -> List[Lead]:
        leads = list(self._leads.values())
        if status:
            return [lead for lead in leads if lead.status == status]
        return leads

    def queue_snapshot(self) -> List[Dict[str, Any]]:
        queue = sorted(self._leads.values(), key=lambda lead: (-lead.priority, lead.created_at))
        return [lead.as_dict() for lead in queue]

    def routing_snapshot(self, rules: List[RoutingRule]) -> List[Dict[str, Any]]:
        snapshot = []
        for lead in self._leads.values():
            item = lead.as_dict()
            item["routing"] = route_lead(lead, rules)
            snapshot.append(item)
        return sorted(snapshot, key=lambda item: (-item["routing"]["priority_with_boost"], item["lead_id"]))

    def stats(self) -> Dict[str, Any]:
        leads = list(self._leads.values())
        status_counts: Dict[str, int] = {}
        budgets = [lead.budget for lead in leads if lead.budget is not None]
        sla_counts: Dict[str, int] = {}
        for lead in leads:
            status_counts[lead.status] = status_counts.get(lead.status, 0) + 1
            bucket = sla_bucket(lead.created_at, lead.priority, lead.status)
            sla_counts[bucket] = sla_counts.get(bucket, 0) + 1
        return {
            "total_leads": len(leads),
            "status_counts": status_counts,
            "average_budget": round(sum(budgets) / len(budgets), 2) if budgets else 0,
            "hot_leads": len([lead for lead in leads if lead.temperature == "hot"]),
            "channels": sorted({classify_channel(lead.source) for lead in leads}),
            "sla_counts": sla_counts,
        }

    def events_for(self, lead_id: str) -> List[Event]:
        return [event for event in self._events if event.lead_id == lead_id]
