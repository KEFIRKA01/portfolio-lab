from datetime import datetime, timedelta, timezone

from app.core import BookingIntent, BookingRouter, Provider, is_after_hours


def build_router() -> BookingRouter:
    return BookingRouter(
        providers=[
            Provider(provider_id="alpha", capabilities=["massage", "consulting"], regions=["moscow"], channels=["site", "telegram"], priority=90),
            Provider(provider_id="bravo", capabilities=["massage"], regions=["moscow", "spb"], channels=["partner", "site"], priority=70),
            Provider(provider_id="night", capabilities=["massage"], regions=["moscow"], channels=["telegram"], priority=95, after_hours=True),
        ]
    )


def test_router_prefers_high_priority_provider() -> None:
    router = build_router()
    intent = BookingIntent(
        booking_id="bk-1",
        service_type="massage",
        channel="site",
        location="moscow",
        start_at=datetime.now(timezone.utc) + timedelta(hours=8),
    )
    decision = router.preview(intent)
    assert decision.provider_id == "alpha"


def test_after_hours_route_uses_night_provider() -> None:
    router = build_router()
    start_at = datetime.now(timezone.utc).replace(hour=22, minute=0, second=0, microsecond=0)
    intent = BookingIntent(
        booking_id="bk-2",
        service_type="massage",
        channel="telegram",
        location="moscow",
        start_at=start_at,
        customer_tier="vip",
    )
    assert is_after_hours(start_at)
    decision = router.preview(intent)
    assert decision.provider_id == "night"
    assert decision.reason == "vip_priority"


def test_slot_conflict_forces_fallback() -> None:
    router = build_router()
    start_at = datetime.now(timezone.utc) + timedelta(hours=10)
    first = BookingIntent("bk-3", "massage", "site", "moscow", start_at)
    second = BookingIntent("bk-4", "massage", "site", "moscow", start_at)
    router.confirm(first)
    decision = router.preview(second)
    assert decision.provider_id == "bravo"
