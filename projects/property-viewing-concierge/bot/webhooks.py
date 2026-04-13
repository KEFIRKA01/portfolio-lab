from __future__ import annotations

from .contracts import WebhookPayload, webhook_event
from .service import AppService

def handle_webhook(service: AppService, source: str, event: str, body: dict) -> dict:
    payload = webhook_event(source=source, event=event, body=body)
    item_id = payload.body.get("item_id")
    note = payload.body.get("note", "")
    if not item_id:
        return {"accepted": False, "reason": "missing item_id"}
    return {"accepted": True, "snapshot": service.webhook_ingest(payload.event, item_id, note=note)}
