from __future__ import annotations

from typing import Iterable

from .analytics import card
from .policies import decision
from .domain import Item, display_label

def admin_snapshot(items: Iterable[Item]) -> dict:
    rows = list(items)
    return {
        "critical": sum(1 for item in rows if card(item).lane == "critical"),
        "manual_review": sum(1 for item in rows if decision(item).requires_manual_review),
        "unassigned": sum(1 for item in rows if item.assigned_to is None),
    }

def priority_board(items: Iterable[Item]) -> list[str]:
    ordered = sorted(rows := list(items), key=lambda item: (card(item).lane, -card(item).chance))
    return [f"{item.item_id} -> {display_label(card(item).lane)} / {display_label(decision(item).owner)}" for item in ordered[:8]]

def exception_board(items: Iterable[Item]) -> list[str]:
    lines = []
    for item in items:
        info = decision(item)
        if info.blockers or info.requires_manual_review:
            lines.append(f"{item.item_id}: {', '.join(info.blockers or ['ручная проверка'])}")
    return lines
