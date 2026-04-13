from __future__ import annotations

from pathlib import Path

from .exports import json_bundle
from .service import AppService
from .webhooks import handle_webhook

try:
    from fastapi import FastAPI
except ImportError:  # pragma: no cover
    FastAPI = None

def create_app():
    if FastAPI is None:
        raise RuntimeError("fastapi is not installed")
    app = FastAPI(title="API проекта «Мост выездного сервиса»", version="1.0.0")
    service = AppService.with_sqlite(Path(__file__).resolve().parents[1] / "seed" / "demo.sqlite3")

    @app.get("/health")
    def health():
        return {"status": "ok", "items": len(service.queue())}

    @app.get("/items")
    def items():
        return {"items": [item.item_id for item in service.queue()], "digest": service.digest()}

    @app.get("/items/{item_id}")
    def item(item_id: str):
        return service.item(item_id)

    @app.post("/seed")
    def seed():
        return {"persisted": service.persist_queue()}

    @app.get("/export/json")
    def export_json():
        return {"payload": json_bundle(service.queue())}

    @app.post("/webhook")
    def webhook(payload: dict):
        return handle_webhook(service, source=payload.get("source", "demo"), event=payload.get("event", "update"), body=payload)

    return app
