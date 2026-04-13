from pathlib import Path
import json


def test_seed_has_project_types_and_modules() -> None:
    payload = json.loads((Path(__file__).resolve().parents[1] / "seed" / "content.json").read_text(encoding="utf-8"))
    assert "project_types" in payload
    assert "modules" in payload
    assert "cabinet" in payload["project_types"]


def test_site_entry_exists() -> None:
    assert (Path(__file__).resolve().parents[1] / "site" / "index.html").exists()
