from __future__ import annotations

from datetime import datetime
from typing import Any

from .core import BookingIntent, BookingRouter, Provider

try:
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
except ImportError:  # pragma: no cover
    FastAPI = None
    HTTPException = RuntimeError
    BaseModel = object


class BookingPayload(BaseModel):
    booking_id: str
    service_type: str
    channel: str
    location: str
    start_at: datetime
    customer_tier: str = "standard"


router = BookingRouter(
    providers=[
        Provider(provider_id="alpha", capabilities=["massage", "consulting"], regions=["moscow"], channels=["site", "telegram"], priority=90),
        Provider(provider_id="bravo", capabilities=["massage"], regions=["moscow", "spb"], channels=["partner", "site"], priority=70),
        Provider(provider_id="night", capabilities=["massage"], regions=["moscow"], channels=["telegram"], priority=95, after_hours=True),
    ]
)
app = FastAPI(title="EventMesh Booking Router") if FastAPI else None


if app:
    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}


    @app.get("/stats")
    def stats() -> dict[str, int]:
        return router.stats()


    @app.post("/preview")
    def preview(payload: BookingPayload) -> dict[str, Any]:
        try:
            return router.preview(BookingIntent(**payload.model_dump())).as_dict()
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc


    @app.post("/bookings")
    def create_booking(payload: BookingPayload) -> dict[str, Any]:
        try:
            return router.confirm(BookingIntent(**payload.model_dump())).as_dict()
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
