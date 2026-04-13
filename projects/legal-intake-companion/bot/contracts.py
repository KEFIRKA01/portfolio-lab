from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

@dataclass(slots=True)
class CommandPayload:
    command: str
    item_id: str | None = None
    actor_id: str | None = None
    note: str = ""

@dataclass(slots=True)
class WebhookPayload:
    event: str
    source: str
    body: Dict[str, Any]

@dataclass(slots=True)
class AuditContract:
    event_name: str
    severity: str
    message: str

def parse_command(command: str, args: list[str]) -> CommandPayload:
    item_id = args[0] if args else None
    actor_id = args[1] if len(args) > 1 else None
    return CommandPayload(command=command, item_id=item_id, actor_id=actor_id)

def webhook_event(source: str, event: str, body: Dict[str, Any]) -> WebhookPayload:
    return WebhookPayload(event=event, source=source, body=body)

def audit_line(event_name: str, severity: str, message: str) -> AuditContract:
    return AuditContract(event_name=event_name, severity=severity, message=message)
