from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Dict, List


@dataclass(slots=True)
class Signal:
    service: str
    kind: str
    severity: str
    owner: str


@dataclass(slots=True)
class Incident:
    incident_id: str
    services: List[str]
    owner: str
    severity: str
    summary: str

    def as_dict(self) -> Dict[str, object]:
        return asdict(self)


def correlate(signals: List[Signal]) -> Incident:
    services = sorted({signal.service for signal in signals})
    severity = "critical" if any(signal.severity == "critical" for signal in signals) else "warning"
    owners = {signal.owner for signal in signals}
    owner = "incident_manager" if len(owners) > 1 else next(iter(owners))
    summary = f"Impacted services: {', '.join(services)}"
    return Incident(incident_id=f"inc-{len(services)}-{severity}", services=services, owner=owner, severity=severity, summary=summary)


def runbook(incident: Incident) -> List[str]:
    actions = [f"Назначить владельца: {incident.owner}", "Открыть war-room канал"]
    if incident.severity == "critical":
        actions.append("Заморозить релизные изменения")
    if len(incident.services) > 1:
        actions.append("Проверить общие интеграции и shared infrastructure")
    return actions
