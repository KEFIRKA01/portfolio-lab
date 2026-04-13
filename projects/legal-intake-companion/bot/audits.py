from __future__ import annotations

from collections import Counter

from .domain import Item

def action_histogram(items: list[Item]) -> dict[str, int]:
    counter: Counter[str] = Counter()
    for item in items:
        for event in item.history:
            counter[event.action] += 1
    return dict(counter)

def anomaly_flags(items: list[Item]) -> list[str]:
    flags: list[str] = []
    if sum(1 for item in items if item.status == "blocked") >= 2:
        flags.append("too_many_blocked")
    if sum(1 for item in items if item.assigned_to is None) >= 3:
        flags.append("unassigned_backlog")
    return flags

def audit_summary(items: list[Item]) -> dict:
    return {"histogram": action_histogram(items), "flags": anomaly_flags(items)}
