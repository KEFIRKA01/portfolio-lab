from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Dict, List


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


ALLOWED_TRANSITIONS = {
    "draft": {"submitted"},
    "submitted": {"in_review", "rejected"},
    "in_review": {"approved", "needs_changes", "rejected"},
    "needs_changes": {"submitted"},
    "approved": set(),
    "rejected": set(),
}

ROLE_PERMISSIONS = {
    "owner": {"approve", "reject", "comment", "upload_document", "change_status"},
    "manager": {"comment", "upload_document", "change_status", "assign"},
    "client": {"comment", "upload_document"},
}

REQUIRED_DOCUMENTS = {
    "submitted": set(),
    "in_review": {"brief.pdf"},
    "approved": {"brief.pdf", "estimate.xlsx"},
}


@dataclass(slots=True)
class ApprovalStep:
    role: str
    reason: str


@dataclass(slots=True)
class RequestCard:
    request_id: str
    title: str
    status: str = "draft"
    documents: List[str] = field(default_factory=list)
    comments: List[str] = field(default_factory=list)
    assigned_to: str | None = None
    priority: str = "normal"
    updated_at: datetime = field(default_factory=utc_now)


@dataclass(slots=True)
class AuditRecord:
    request_id: str
    actor: str
    action: str
    created_at: datetime = field(default_factory=utc_now)


def can(role: str, action: str) -> bool:
    return action in ROLE_PERMISSIONS.get(role, set())


def can_transition(current_status: str, next_status: str) -> bool:
    return next_status in ALLOWED_TRANSITIONS.get(current_status, set())


def missing_documents_for(card: RequestCard, next_status: str) -> List[str]:
    required = REQUIRED_DOCUMENTS.get(next_status, set())
    present = set(card.documents)
    return sorted(required - present)


def document_completeness(card: RequestCard, next_status: str) -> int:
    required = REQUIRED_DOCUMENTS.get(next_status, set())
    if not required:
        return 100
    missing = set(missing_documents_for(card, next_status))
    return round(((len(required) - len(missing)) / len(required)) * 100)


def build_approval_plan(card: RequestCard) -> List[ApprovalStep]:
    title = card.title.lower()
    plan = [ApprovalStep(role="manager", reason="Базовая проверка процесса и бюджета")]
    if "безопас" in title or "security" in title:
        plan.append(ApprovalStep(role="security", reason="Проверка чувствительных доступов"))
    if "white-label" in title or "white label" in title:
        plan.append(ApprovalStep(role="owner", reason="Подтверждение нестандартной OEM/white-label схемы"))
    if card.priority == "high":
        plan.append(ApprovalStep(role="finance", reason="Проверка повышенного приоритета и нагрузки"))
    return plan


def escalation_reason(card: RequestCard, now: datetime | None = None) -> str | None:
    current_time = now or utc_now()
    if card.priority == "high" and not card.assigned_to:
        return "Высокий приоритет без назначенного менеджера"
    if card.status in {"submitted", "in_review"} and current_time - card.updated_at > timedelta(hours=24):
        return "Карточка зависла без движения больше 24 часов"
    return None


class RequestStore:
    def __init__(self) -> None:
        self._cards: Dict[str, RequestCard] = {}
        self._audit: List[AuditRecord] = []

    def add(self, card: RequestCard) -> None:
        self._cards[card.request_id] = card
        self._audit.append(AuditRecord(request_id=card.request_id, actor="system", action="created"))

    def get(self, request_id: str) -> RequestCard:
        return self._cards[request_id]

    def comment(self, request_id: str, text: str) -> None:
        card = self._cards[request_id]
        card.comments.append(text)
        card.updated_at = utc_now()
        self._audit.append(AuditRecord(request_id=request_id, actor="user", action="commented"))

    def upload_document(self, request_id: str, name: str) -> None:
        card = self._cards[request_id]
        if name not in card.documents:
            card.documents.append(name)
        card.updated_at = utc_now()
        self._audit.append(AuditRecord(request_id=request_id, actor="user", action=f"document:{name}"))

    def assign(self, request_id: str, manager_name: str) -> None:
        card = self._cards[request_id]
        card.assigned_to = manager_name
        card.updated_at = utc_now()
        self._audit.append(AuditRecord(request_id=request_id, actor="manager", action=f"assigned:{manager_name}"))

    def transition(self, request_id: str, next_status: str) -> None:
        card = self._cards[request_id]
        if not can_transition(card.status, next_status):
            raise ValueError(f"Cannot move {card.status} -> {next_status}")
        missing = missing_documents_for(card, next_status)
        if missing:
            raise ValueError(f"Missing required documents: {', '.join(missing)}")
        card.status = next_status
        card.updated_at = utc_now()
        self._audit.append(AuditRecord(request_id=request_id, actor="manager", action=f"status:{next_status}"))

    def list_cards(self) -> List[RequestCard]:
        return sorted(self._cards.values(), key=lambda card: (card.priority, card.updated_at), reverse=True)

    def audit_for(self, request_id: str) -> List[AuditRecord]:
        return [record for record in self._audit if record.request_id == request_id]

    def summary(self, now: datetime | None = None) -> Dict[str, object]:
        cards = list(self._cards.values())
        by_status: Dict[str, int] = {}
        escalated = 0
        for card in cards:
            by_status[card.status] = by_status.get(card.status, 0) + 1
            if escalation_reason(card, now=now):
                escalated += 1
        return {
            "total_requests": len(cards),
            "assigned_requests": len([card for card in cards if card.assigned_to]),
            "status_counts": by_status,
            "escalated_requests": escalated,
        }
