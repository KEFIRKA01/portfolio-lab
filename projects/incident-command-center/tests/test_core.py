from center.core import Signal, correlate, runbook


def test_correlate_merges_services_into_incident() -> None:
    incident = correlate(
        [
            Signal(service="crm", kind="latency", severity="warning", owner="integrations"),
            Signal(service="payments", kind="errors", severity="critical", owner="backend"),
        ]
    )
    assert incident.severity == "critical"
    assert incident.owner == "incident_manager"
    assert "crm" in incident.services


def test_runbook_expands_for_multi_service_critical_incident() -> None:
    incident = correlate(
        [
            Signal(service="crm", kind="latency", severity="warning", owner="integrations"),
            Signal(service="payments", kind="errors", severity="critical", owner="backend"),
        ]
    )
    actions = runbook(incident)
    assert "Заморозить релизные изменения" in actions
    assert "Проверить общие интеграции и shared infrastructure" in actions
