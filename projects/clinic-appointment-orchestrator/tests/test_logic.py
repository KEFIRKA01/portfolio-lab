from __future__ import annotations

from bot.analytics import card, digest
from bot.domain import blueprints, lane
from bot.seeds import load_seed
from bot.storage import Store

def build_store() -> Store:
    actors, items = load_seed()
    store = Store()
    store.seed(actors, items)
    return store

def test_seed_loads_items() -> None:
    actors, items = load_seed()
    assert actors
    assert len(items) >= 3

def test_queue_has_lane() -> None:
    store = build_store()
    assert lane(store.queue()[0]) in {"critical", "priority", "execution", "standard"}

def test_card_contains_scores() -> None:
    store = build_store()
    row = card(store.queue()[0])
    assert 0 < row.risk <= 100
    assert 0 < row.chance <= 95

def test_digest_has_metrics() -> None:
    store = build_store()
    stats = digest(store.queue())
    assert "avg_chance" in stats

def test_has_blueprints() -> None:
    assert len(blueprints()) >= 5
