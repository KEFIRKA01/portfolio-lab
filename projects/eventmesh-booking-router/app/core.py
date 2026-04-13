from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Dict, List


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def is_after_hours(start_at: datetime) -> bool:
    return start_at.hour < 9 or start_at.hour >= 20


@dataclass(slots=True)
class BookingIntent:
    booking_id: str
    service_type: str
    channel: str
    location: str
    start_at: datetime
    customer_tier: str = "standard"

    def urgency(self, now: datetime | None = None) -> str:
        current_time = now or utc_now()
        if self.start_at - current_time <= timedelta(hours=6):
            return "urgent"
        return "normal"


@dataclass(slots=True)
class Provider:
    provider_id: str
    capabilities: List[str]
    regions: List[str]
    channels: List[str]
    priority: int
    after_hours: bool = False


@dataclass(slots=True)
class SlotReservation:
    provider_id: str
    start_at: datetime
    booking_id: str


@dataclass(slots=True)
class RouteDecision:
    provider_id: str
    reason: str
    fallback_chain: List[str] = field(default_factory=list)

    def as_dict(self) -> Dict[str, object]:
        return asdict(self)


class BookingRouter:
    def __init__(self, providers: List[Provider]) -> None:
        self._providers = {provider.provider_id: provider for provider in providers}
        self._slots: List[SlotReservation] = []

    def compatible_providers(self, intent: BookingIntent) -> List[Provider]:
        matches = []
        for provider in self._providers.values():
            if intent.service_type not in provider.capabilities:
                continue
            if intent.location not in provider.regions:
                continue
            if intent.channel not in provider.channels:
                continue
            if is_after_hours(intent.start_at) and not provider.after_hours:
                continue
            matches.append(provider)
        return sorted(matches, key=lambda provider: provider.priority, reverse=True)

    def is_slot_available(self, provider_id: str, start_at: datetime) -> bool:
        return all(
            reservation.provider_id != provider_id or reservation.start_at != start_at
            for reservation in self._slots
        )

    def preview(self, intent: BookingIntent) -> RouteDecision:
        compatible = self.compatible_providers(intent)
        fallback_chain = [provider.provider_id for provider in compatible]
        for provider in compatible:
            if self.is_slot_available(provider.provider_id, intent.start_at):
                reason = "vip_priority" if intent.customer_tier == "vip" else intent.urgency()
                return RouteDecision(provider_id=provider.provider_id, reason=reason, fallback_chain=fallback_chain)
        raise ValueError("No available provider for the selected slot")

    def confirm(self, intent: BookingIntent) -> RouteDecision:
        decision = self.preview(intent)
        self._slots.append(
            SlotReservation(provider_id=decision.provider_id, start_at=intent.start_at, booking_id=intent.booking_id)
        )
        return decision

    def stats(self) -> Dict[str, int]:
        return {
            "providers": len(self._providers),
            "reservations": len(self._slots),
            "after_hours_capable": len([provider for provider in self._providers.values() if provider.after_hours]),
        }
