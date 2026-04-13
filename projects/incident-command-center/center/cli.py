from __future__ import annotations

import json

from .core import Signal, correlate, runbook


def main() -> None:
    signals = [
        Signal(service="crm", kind="latency", severity="warning", owner="integrations"),
        Signal(service="payments", kind="errors", severity="critical", owner="backend"),
    ]
    incident = correlate(signals)
    print(json.dumps({"incident": incident.as_dict(), "runbook": runbook(incident)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
