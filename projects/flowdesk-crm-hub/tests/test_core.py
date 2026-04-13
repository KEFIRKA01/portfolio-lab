from datetime import datetime, timedelta, timezone

from app.core import (
    Lead,
    LeadStore,
    RoutingRule,
    build_signature,
    classify_channel,
    infer_tags,
    normalize_phone,
    route_lead,
    sla_bucket,
)


def test_normalize_phone_rewrites_russian_mobile() -> None:
    assert normalize_phone("+7 (999) 123-45-67") == "79991234567"
    assert normalize_phone("8 (999) 123-45-67") == "79991234567"


def test_signature_is_stable() -> None:
    first = build_signature("Иван", "+7 999 123 45 67", "landing-main")
    second = build_signature("иван", "8 (999) 123-45-67", "landing-main")
    assert first == second


def test_duplicate_guard_keeps_original_lead() -> None:
    store = LeadStore()
    first = Lead(lead_id="lead-1", name="Иван", phone="+7 999 123 45 67", source="landing-main")
    second = Lead(lead_id="lead-2", name="Иван", phone="8 999 123 45 67", source="landing-main")
    created_id = store.add_lead(first)
    duplicate_id = store.add_lead(second)
    assert created_id == "lead-1"
    assert duplicate_id == "lead-1"
    assert len(store.all_leads()) == 1
    assert classify_channel("telegram-bot") == "telegram"


def test_lead_tags_and_priority_are_inferred_from_note_and_budget() -> None:
    lead = Lead(
        lead_id="lead-9",
        name="Ольга",
        phone="+7 999 111 22 33",
        source="telegram-bot",
        budget=180_000,
        note="Срочно нужно подключить CRM и webhook для B2B клиента",
    )
    assert {"crm", "api", "urgent", "enterprise"} <= set(infer_tags(lead.source, lead.budget, lead.note))
    assert lead.temperature == "hot"
    assert lead.priority >= 50


def test_status_transition_validation_and_stats() -> None:
    store = LeadStore()
    lead = Lead(lead_id="lead-3", name="Мария", phone="+7 999 000 11 22", source="landing-main", budget=90_000)
    store.add_lead(lead)
    store.update_status("lead-3", "qualified")
    store.update_status("lead-3", "proposal_sent")
    stats = store.stats()
    assert stats["total_leads"] == 1
    assert stats["status_counts"]["proposal_sent"] == 1


def test_queue_snapshot_orders_more_promising_leads_first() -> None:
    store = LeadStore()
    store.add_lead(Lead(lead_id="cold", name="Игорь", phone="+7 999 100 00 00", source="site-manual"))
    store.add_lead(
        Lead(
            lead_id="hot",
            name="Анна",
            phone="+7 999 200 00 00",
            source="telegram-bot",
            budget=220_000,
            note="Нужно срочно настроить CRM и API",
        )
    )
    queue = store.queue_snapshot()
    assert queue[0]["lead_id"] == "hot"


def test_route_lead_supports_unusual_enterprise_and_white_label_rules() -> None:
    lead = Lead(
        lead_id="wl-1",
        name="Павел",
        phone="+7 999 333 00 00",
        source="telegram-bot",
        budget=260_000,
        note="Нужен white-label B2B сервис с CRM и API",
    )
    lead.tags = infer_tags(lead.source, lead.budget, lead.note)
    rules = [
        RoutingRule(name="enterprise_crm", destination="enterprise_team", required_tags=["crm", "enterprise"], min_budget=150_000, priority_boost=12),
        RoutingRule(name="white_label", destination="special_projects", required_tags=["white_label"], channels=["telegram"], min_budget=200_000, priority_boost=18),
    ]
    result = route_lead(lead, rules)
    assert result["destination"] == "special_projects"
    assert "white_label" in result["matched_rules"]
    assert result["priority_with_boost"] > lead.priority


def test_sla_bucket_detects_breach_risk_for_aged_hot_lead() -> None:
    created_at = datetime.now(timezone.utc) - timedelta(hours=2)
    assert sla_bucket(created_at, priority=80, status="new") == "breach_risk"
