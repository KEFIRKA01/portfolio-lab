from __future__ import annotations

from dataclasses import dataclass

from .analytics import card
from .domain import CATEGORIES, Item

@dataclass(slots=True)
class BenchmarkCase:
    name: str
    target_sla_minutes: int
    target_chance: int
    target_fit: int
    comment: str

def default_cases() -> list[BenchmarkCase]:
    return [
        BenchmarkCase("critical-escalation", 15, 72, 68, "ручной high-priority контур"),
        BenchmarkCase("priority-throughput", 45, 70, 64, "быстрый проход по приоритетной очереди"),
        BenchmarkCase("execution-stability", 180, 78, 60, "стабильное закрытие execution кейсов"),
        BenchmarkCase("manual-review", 30, 55, 58, "контроль risky сценариев"),
        BenchmarkCase("backlog-drain", 240, 62, 52, "снижение хвоста без просадки SLA"),
    ]

def capacity_model(items: list[Item]) -> dict[str, int]:
    return {
        "critical_slots": max(1, sum(1 for item in items if card(item).lane == "critical")),
        "priority_slots": max(2, sum(1 for item in items if card(item).lane == "priority")),
        "standard_slots": max(3, sum(1 for item in items if card(item).lane == "standard")),
    }

def quality_gates(items: list[Item]) -> list[str]:
    gates: list[str] = []
    if sum(1 for item in items if item.category in CATEGORIES[:2]) >= 2:
        gates.append("priority_lane_covered")
    if sum(1 for item in items if len(item.signals) >= 2) >= 1:
        gates.append("risk_signals_present")
    if sum(1 for item in items if item.assigned_to is None) <= max(2, len(items) // 2):
        gates.append("assignment_is_balanced")
    return gates

def benchmark_report(items: list[Item]) -> dict:
    return {
        "cases": [case.name for case in default_cases()],
        "capacity": capacity_model(items),
        "quality_gates": quality_gates(items),
    }
