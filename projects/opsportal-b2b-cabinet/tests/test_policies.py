from datetime import datetime, timedelta, timezone

import pytest

from app.policies import (
    RequestCard,
    RequestStore,
    build_approval_plan,
    can,
    can_transition,
    document_completeness,
    escalation_reason,
    missing_documents_for,
)


def test_role_permissions() -> None:
    assert can("owner", "approve")
    assert can("manager", "change_status")
    assert not can("client", "change_status")


def test_transition_matrix() -> None:
    assert can_transition("draft", "submitted")
    assert not can_transition("approved", "submitted")


def test_store_updates_comments_and_documents() -> None:
    store = RequestStore()
    store.add(RequestCard(request_id="req-1", title="Demo"))
    store.comment("req-1", "Нужно уточнить состав документов")
    store.upload_document("req-1", "invoice.pdf")
    card = store.get("req-1")
    assert card.comments == ["Нужно уточнить состав документов"]
    assert card.documents == ["invoice.pdf"]


def test_transition_to_review_requires_brief() -> None:
    store = RequestStore()
    store.add(RequestCard(request_id="req-2", title="Demo", status="submitted"))
    with pytest.raises(ValueError):
        store.transition("req-2", "in_review")
    store.upload_document("req-2", "brief.pdf")
    store.transition("req-2", "in_review")
    assert store.get("req-2").status == "in_review"


def test_assign_and_audit_summary() -> None:
    store = RequestStore()
    store.add(RequestCard(request_id="req-3", title="B2B cabinet"))
    store.assign("req-3", "Никита")
    summary = store.summary()
    assert summary["assigned_requests"] == 1
    assert missing_documents_for(store.get("req-3"), "approved") == ["brief.pdf", "estimate.xlsx"]
    assert len(store.audit_for("req-3")) >= 2


def test_approval_plan_covers_white_label_and_high_priority_paths() -> None:
    card = RequestCard(request_id="req-4", title="White-label security cabinet", priority="high")
    plan_roles = [step.role for step in build_approval_plan(card)]
    assert {"manager", "security", "owner", "finance"} <= set(plan_roles)


def test_document_completeness_and_escalation() -> None:
    stale_time = datetime.now(timezone.utc) - timedelta(hours=30)
    card = RequestCard(request_id="req-5", title="Enterprise flow", status="submitted", updated_at=stale_time)
    assert document_completeness(card, "approved") == 0
    assert escalation_reason(card, now=datetime.now(timezone.utc)) == "Карточка зависла без движения больше 24 часов"
