from __future__ import annotations

from pathlib import Path

from .analytics import digest
from .domain import Item, blueprints, normalize_tags, snapshot, utc_now
from .repository_sqlite import SQLiteRepository
from .seeds import load_seed
from .storage import Store

class AppService:
    def __init__(self, store: Store | None = None, repository: SQLiteRepository | None = None) -> None:
        self.store = store or self.build_store()
        self.repository = repository

    @staticmethod
    def build_store() -> Store:
        store = Store()
        actors, items = load_seed()
        store.seed(actors, items)
        return store

    @classmethod
    def with_sqlite(cls, db_path: str | Path):
        return cls(repository=SQLiteRepository(db_path))

    def queue(self):
        return self.store.queue()

    def digest(self) -> dict:
        return digest(self.store.queue())

    def item(self, item_id: str) -> Item:
        return self.store.get(item_id)

    def create_dynamic_item(self) -> Item:
        blueprint = blueprints()[len(self.store.queue()) % len(blueprints())]
        record = Item(
            item_id="dynamic-" + str(len(self.store.queue()) + 1),
            customer_name="Демо-пользователь",
            title=blueprint.name + " / сервис",
            category=blueprint.category,
            status="new",
            priority=61,
            budget=24500,
            deadline_at=utc_now(),
            tags=normalize_tags([blueprint.category, blueprint.feature]),
            signals=["демо-сервис", blueprint.risk],
            notes=["создано сервисным слоем"],
            metadata={"scenario": blueprint.name, "source": "service"},
        )
        self.store.add_item(record)
        return record

    def persist_queue(self) -> int:
        if not self.repository:
            return 0
        self.repository.upsert_many(self.store.queue())
        return self.repository.count()

    def webhook_ingest(self, event: str, item_id: str, note: str = "") -> dict:
        item = self.store.get(item_id)
        item.add_signal(event)
        if note:
            item.add_note(note)
        if self.repository:
            self.repository.upsert_item(item)
        return snapshot(item)
