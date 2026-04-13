from pathlib import Path
import json


def test_content_contract_has_hero_and_cta() -> None:
    payload = json.loads(
        (Path(__file__).resolve().parents[1] / "seed" / "content.json").read_text(encoding="utf-8")
    )
    assert "hero" in payload
    assert "cta" in payload
    assert payload["hero"]["title"]


def test_site_entry_exists() -> None:
    assert (Path(__file__).resolve().parents[1] / "site" / "index.html").exists()
