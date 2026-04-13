from __future__ import annotations

from typing import Any

from .core import Lead, LeadStore, RoutingRule

try:
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel, Field
except ImportError:  # pragma: no cover
    FastAPI = None
    HTTPException = RuntimeError
    BaseModel = object
    Field = None


class LeadPayload(BaseModel):
    lead_id: str
    name: str
    phone: str
    source: str
    note: str | None = None
    budget: int | None = None


class StatusPayload(BaseModel):
    status: str


class NotePayload(BaseModel):
    note: str


class PaymentPayload(BaseModel):
    lead_id: str
    amount: int
    gateway: str


class RoutingRulePayload(BaseModel):
    name: str
    destination: str
    required_tags: list[str] = Field(default_factory=list)
    channels: list[str] = Field(default_factory=list)
    min_budget: int = 0
    priority_boost: int = 0


store = LeadStore()
app = FastAPI(title="FlowDesk CRM Hub") if FastAPI else None


if app:
    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}


    @app.get("/stats")
    def stats() -> dict[str, Any]:
        return store.stats()


    @app.get("/queue")
    def queue_snapshot() -> list[dict[str, Any]]:
        return store.queue_snapshot()


    @app.post("/routing/preview")
    def routing_preview(payload: list[RoutingRulePayload]) -> list[dict[str, Any]]:
        rules = [RoutingRule(**item.model_dump()) for item in payload]
        return store.routing_snapshot(rules)


    @app.get("/leads")
    def list_leads(status: str | None = None) -> list[dict[str, Any]]:
        return [lead.as_dict() for lead in store.all_leads(status=status)]


    @app.post("/leads")
    def create_lead(payload: LeadPayload) -> dict[str, str]:
        lead = Lead(**payload.model_dump())
        lead_id = store.add_lead(lead)
        return {"lead_id": lead_id}


    @app.post("/leads/{lead_id}/status")
    def change_status(lead_id: str, payload: StatusPayload) -> dict[str, str]:
        known_ids = {lead.lead_id for lead in store.all_leads()}
        if lead_id not in known_ids:
            raise HTTPException(status_code=404, detail="Lead not found")
        try:
            store.update_status(lead_id, payload.status)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return {"lead_id": lead_id, "status": payload.status}


    @app.post("/leads/{lead_id}/note")
    def update_note(lead_id: str, payload: NotePayload) -> dict[str, str]:
        known_ids = {lead.lead_id for lead in store.all_leads()}
        if lead_id not in known_ids:
            raise HTTPException(status_code=404, detail="Lead not found")
        store.append_note(lead_id, payload.note)
        return {"lead_id": lead_id, "status": "note_updated"}


    @app.post("/webhooks/payment")
    def payment_callback(payload: PaymentPayload) -> dict[str, str]:
        known_ids = {lead.lead_id for lead in store.all_leads()}
        if payload.lead_id not in known_ids:
            raise HTTPException(status_code=404, detail="Lead not found")
        store.record_payment(payload.lead_id, payload.amount, payload.gateway)
        return {"lead_id": payload.lead_id, "status": "payment_recorded"}


    @app.get("/leads/{lead_id}/events")
    def lead_events(lead_id: str) -> list[dict[str, Any]]:
        return [event.as_dict() for event in store.events_for(lead_id)]
