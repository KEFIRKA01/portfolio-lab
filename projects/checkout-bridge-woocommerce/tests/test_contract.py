from pathlib import Path
import json


def test_demo_settings_have_required_keys() -> None:
    settings_path = Path(__file__).resolve().parents[1] / "assets" / "demo-settings.json"
    payload = json.loads(settings_path.read_text(encoding="utf-8"))
    assert set(payload) == {"webhook_url", "telegram_url", "sync_mode", "sync_profile"}


def test_plugin_file_exists() -> None:
    plugin_path = Path(__file__).resolve().parents[1] / "plugin" / "checkout-bridge-for-woocommerce.php"
    assert plugin_path.exists()


def test_plugin_contains_retry_queue_logic() -> None:
    plugin_path = Path(__file__).resolve().parents[1] / "plugin" / "checkout-bridge-for-woocommerce.php"
    plugin_source = plugin_path.read_text(encoding="utf-8")
    assert "cbfw_retry_queue" in plugin_source
    assert "Retry failed deliveries" in plugin_source
    assert "idempotency_key" in plugin_source
    assert "sync_profile" in plugin_source
