from __future__ import annotations

import json
from typing import Iterable

from .analytics import card
from .domain import Item, display_label, snapshot

def csv_lines(items: Iterable[Item]) -> str:
    rows = ["item_id,category,status,lane,chance,value"]
    for item in items:
        row = card(item)
        rows.append(f"{item.item_id},{item.category},{item.status},{row.lane},{row.chance},{row.value}")
    return "\n".join(rows)

def json_bundle(items: Iterable[Item]) -> str:
    return json.dumps([snapshot(item) for item in items], ensure_ascii=False, indent=2)

def public_case_summary(items: Iterable[Item]) -> str:
    lines = ["Краткая витринная сводка:"]
    for item in list(items)[:5]:
        row = card(item)
        lines.append(f"- {item.title}: очередь={display_label(row.lane)}, шанс={row.chance}, время={row.effort} ч")
    return "\n".join(lines)
