from pathlib import Path
import json


def test_demo_settings_have_required_keys() -> None:
    payload = json.loads((Path(__file__).resolve().parents[1] / "assets" / "demo-settings.json").read_text(encoding="utf-8"))
    assert set(payload) == {"webhook_url", "sync_profile"}


def test_plugin_contains_refund_and_retry_logic() -> None:
    plugin_source = (Path(__file__).resolve().parents[1] / "plugin" / "returns-sync-for-woocommerce.php").read_text(encoding="utf-8")
    assert "woocommerce_order_refunded" in plugin_source
    assert "rsfw_retry_queue" in plugin_source
    assert "idempotency_key" in plugin_source
