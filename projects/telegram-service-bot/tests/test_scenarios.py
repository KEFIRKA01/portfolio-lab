from datetime import datetime, timedelta, timezone

from bot.scenarios import (
    RequestBoard,
    ServiceRequest,
    can_transition,
    infer_flow_type,
    manager_alert_text,
    next_actions,
    reminder_due,
    required_inputs,
    suggest_reply,
)


def test_transition_map() -> None:
    assert can_transition("new", "qualified")
    assert not can_transition("done", "new")


def test_manager_alert_contains_main_fields() -> None:
    request = ServiceRequest(request_id="tg-1", customer_name="Ирина", summary="Нужен бот")
    text = manager_alert_text(request)
    assert "Ирина" in text
    assert "Нужен бот" in text


def test_reminder_due_adds_hours() -> None:
    created = datetime(2026, 1, 1, tzinfo=timezone.utc)
    assert reminder_due(created, hours=6).hour == 6
    assert next_actions("qualified") == ["подготовить предложение", "согласовать этапы"]


def test_request_board_tracks_priority_and_reminders() -> None:
    board = RequestBoard()
    request = ServiceRequest(
        request_id="tg-2",
        customer_name="Павел",
        summary="Срочно нужен Telegram-бот для заявок",
        created_at=datetime.now(timezone.utc) - timedelta(hours=13),
    )
    board.add(request)
    board.transition("tg-2", "qualified", "Проверили вводные")
    board.transition("tg-2", "in_progress", "Взяли в работу")
    board.transition("tg-2", "waiting_customer", "Ждём подтверждение от клиента")
    digest = board.digest()
    assert digest["high_priority"] == 1
    assert len(board.reminder_candidates(datetime.now(timezone.utc))) == 1


def test_unusual_partner_portal_flow_has_specific_requirements() -> None:
    request = ServiceRequest(request_id="tg-3", customer_name="Лев", summary="Нужен white-label кабинет для партнёров")
    assert infer_flow_type(request.summary) == "partner_portal"
    assert "white-label" in suggest_reply(request)
    assert "сценарий white-label" in required_inputs("partner_portal")
