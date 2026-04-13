from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Iterable

from .domain import Item, snapshot

class SQLiteRepository:
    def __init__(self, db_path: str | Path) -> None:
        self.db_path = str(db_path)
        self._ensure_schema()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _ensure_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                '''
                create table if not exists items (
                    item_id text primary key,
                    category text not null,
                    status text not null,
                    payload text not null
                )
                '''
            )
            conn.commit()

    def upsert_item(self, item: Item) -> None:
        payload = json.dumps(snapshot(item), ensure_ascii=False)
        with self._connect() as conn:
            conn.execute(
                "insert into items(item_id, category, status, payload) values (?, ?, ?, ?) "
                "on conflict(item_id) do update set category=excluded.category, status=excluded.status, payload=excluded.payload",
                (item.item_id, item.category, item.status, payload),
            )
            conn.commit()

    def upsert_many(self, items: Iterable[Item]) -> None:
        for item in items:
            self.upsert_item(item)

    def fetch_item(self, item_id: str) -> dict | None:
        with self._connect() as conn:
            row = conn.execute("select payload from items where item_id = ?", (item_id,)).fetchone()
        return json.loads(row[0]) if row else None

    def list_items(self) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute("select payload from items order by item_id").fetchall()
        return [json.loads(row[0]) for row in rows]

    def count(self) -> int:
        with self._connect() as conn:
            row = conn.execute("select count(*) from items").fetchone()
        return int(row[0]) if row else 0
