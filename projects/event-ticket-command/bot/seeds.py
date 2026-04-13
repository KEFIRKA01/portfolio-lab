from __future__ import annotations

import json
from datetime import timedelta
from pathlib import Path

from .domain import Actor, Item, normalize_tags, utc_now

SEED = Path(__file__).resolve().parents[1] / "seed" / "demo_seed.json"

def load_seed() -> tuple[list[Actor], list[Item]]:
    payload = json.loads(SEED.read_text(encoding="utf-8"))
    actors = [Actor(actor_id=row["actor_id"], name=row["name"], role=row["role"], segment=row["segment"], trust=row.get("trust", 50), flags=row.get("flags", [])) for row in payload["actors"]]
    items: list[Item] = []
    for row in payload["items"]:
        items.append(Item(
            item_id=row["item_id"],
            customer_name=row["customer_name"],
            title=row["title"],
            category=row["category"],
            status=row.get("status", "new"),
            priority=row.get("priority", 40),
            budget=row.get("budget", 0),
            deadline_at=utc_now() + timedelta(hours=row.get("deadline_hours", 8)),
            tags=normalize_tags(row.get("tags", [])),
            signals=row.get("signals", []),
            notes=row.get("notes", []),
            metadata=row.get("metadata", {}),
        ))
    return actors, items
