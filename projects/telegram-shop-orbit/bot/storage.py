from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta
from typing import Dict, Iterable, List

from .domain import Actor, Item, lane, snapshot, summary, utc_now

class Store:
    def __init__(self) -> None:
        self.actors: Dict[str, Actor] = {}
        self.items: Dict[str, Item] = {}

    def seed(self, actors: Iterable[Actor], items: Iterable[Item]) -> None:
        for actor in actors:
            self.actors[actor.actor_id] = actor
        for item in items:
            self.items[item.item_id] = item

    def add_item(self, item: Item) -> None:
        self.items[item.item_id] = item
        item.add_event("created", "system", item.title)

    def get(self, item_id: str) -> Item:
        return self.items[item_id]

    def list(self) -> List[Item]:
        return sorted(self.items.values(), key=lambda item: (item.deadline_at, -item.priority))

    def queue(self) -> List[Item]:
        order = {"critical": 0, "priority": 1, "execution": 2, "standard": 3}
        return sorted(self.list(), key=lambda item: (order.get(lane(item), 4), item.deadline_at, -item.priority))

    def clone(self, item_id: str, new_id: str) -> Item:
        source = self.items[item_id]
        copy = replace(source, item_id=new_id, notes=list(source.notes), signals=list(source.signals), tags=list(source.tags), history=list(source.history))
        copy.add_event("cloned", "system", item_id)
        self.items[new_id] = copy
        return copy

    def assign(self, item_id: str, actor_id: str, author: str = "manager") -> None:
        item = self.items[item_id]
        item.assigned_to = actor_id
        item.status = "assigned"
        item.add_event("assigned", author, actor_id)

    def set_status(self, item_id: str, status: str, author: str = "manager") -> None:
        item = self.items[item_id]
        item.status = status
        item.add_event("status", author, status)

    def add_note(self, item_id: str, note: str, author: str = "manager") -> None:
        self.items[item_id].add_note(note, author=author)

    def add_signal(self, item_id: str, signal: str, author: str = "system") -> None:
        self.items[item_id].add_signal(signal, author=author)

    def postpone(self, item_id: str, hours: int, author: str = "manager") -> None:
        item = self.items[item_id]
        item.deadline_at += timedelta(hours=hours)
        item.add_event("postponed", author, f"{hours}h")

    def escalate(self, item_id: str, reason: str, author: str = "manager") -> None:
        item = self.items[item_id]
        item.status = "escalated"
        item.add_signal(reason, author=author)
        item.add_event("escalated", author, reason)

    def resolve(self, item_id: str, author: str = "manager") -> None:
        item = self.items[item_id]
        item.status = "resolved"
        item.add_event("resolved", author, "done")

    def due_soon(self, now: datetime | None = None, window_hours: int = 8) -> List[Item]:
        now = now or utc_now()
        limit = now + timedelta(hours=window_hours)
        return [item for item in self.queue() if item.status not in {"resolved", "archived"} and item.deadline_at <= limit]

    def unresolved(self) -> List[Item]:
        return [item for item in self.queue() if item.status not in {"resolved", "archived"}]

    def digest(self) -> dict:
        base = summary(self.unresolved())
        base["unassigned"] = sum(1 for item in self.unresolved() if item.assigned_to is None)
        base["due_soon"] = len(self.due_soon())
        return base

    def export(self) -> List[dict]:
        return [snapshot(item) for item in self.queue()]
