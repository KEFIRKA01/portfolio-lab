from __future__ import annotations

from typing import Any

from .policies import RequestCard, RequestStore, build_approval_plan, can, document_completeness, escalation_reason

try:
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
except ImportError:  # pragma: no cover
    FastAPI = None
    HTTPException = RuntimeError
    BaseModel = object


class CreateRequestPayload(BaseModel):
    request_id: str
    title: str
    priority: str = "normal"


class ActionPayload(BaseModel):
    role: str
    value: str


store = RequestStore()
app = FastAPI(title="OpsPortal B2B Cabinet") if FastAPI else None


if app:
    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}


    @app.get("/summary")
    def summary() -> dict[str, Any]:
        return store.summary()


    @app.get("/requests")
    def list_requests() -> list[dict[str, Any]]:
        return [
            {
                "request_id": card.request_id,
                "title": card.title,
                "status": card.status,
                "assigned_to": card.assigned_to,
                "documents": card.documents,
                "comments": card.comments,
                "priority": card.priority,
                "approval_plan": [{"role": step.role, "reason": step.reason} for step in build_approval_plan(card)],
                "escalation_reason": escalation_reason(card),
            }
            for card in store.list_cards()
        ]


    @app.post("/requests")
    def create_request(payload: CreateRequestPayload) -> dict[str, str]:
        store.add(RequestCard(request_id=payload.request_id, title=payload.title, priority=payload.priority))
        return {"request_id": payload.request_id}


    @app.post("/requests/{request_id}/comments")
    def add_comment(request_id: str, payload: ActionPayload) -> dict[str, str]:
        if not can(payload.role, "comment"):
            raise HTTPException(status_code=403, detail="Forbidden")
        store.comment(request_id, payload.value)
        return {"request_id": request_id, "action": "commented"}


    @app.post("/requests/{request_id}/documents")
    def add_document(request_id: str, payload: ActionPayload) -> dict[str, str]:
        if not can(payload.role, "upload_document"):
            raise HTTPException(status_code=403, detail="Forbidden")
        store.upload_document(request_id, payload.value)
        return {"request_id": request_id, "action": "uploaded"}


    @app.post("/requests/{request_id}/status")
    def change_status(request_id: str, payload: ActionPayload) -> dict[str, Any]:
        if not can(payload.role, "change_status"):
            raise HTTPException(status_code=403, detail="Forbidden")
        try:
            store.transition(request_id, payload.value)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        card = store.get(request_id)
        return {
            "request_id": request_id,
            "status": card.status,
            "document_completeness": document_completeness(card, card.status),
        }


    @app.post("/requests/{request_id}/assign")
    def assign_request(request_id: str, payload: ActionPayload) -> dict[str, str]:
        if not can(payload.role, "assign"):
            raise HTTPException(status_code=403, detail="Forbidden")
        store.assign(request_id, payload.value)
        return {"request_id": request_id, "assigned_to": payload.value}


    @app.get("/requests/{request_id}/audit")
    def audit(request_id: str) -> list[dict[str, str]]:
        return [
            {
                "actor": record.actor,
                "action": record.action,
                "created_at": record.created_at.isoformat(),
            }
            for record in store.audit_for(request_id)
        ]
