import logging

from app.config import Settings
from app.core.alerts import AlertNotifier


def _settings(**overrides) -> Settings:
    base = dict(
        postgres_password="x",
        admin_username="admin",
        admin_password="x",
        jwt_secret_key="x",
    )
    base.update(overrides)
    return Settings(**base)


def test_disabled_without_credentials():
    notifier = AlertNotifier(_settings())
    assert notifier.enabled is False


def test_disabled_notify_only_logs(caplog):
    notifier = AlertNotifier(_settings())
    with caplog.at_level(logging.INFO):
        notifier.notify_error(source="test", detail="boom")
    assert "заглушка" in caplog.text
    assert "boom" in caplog.text


def test_enabled_with_both_token_and_chat_id():
    notifier = AlertNotifier(_settings(telegram_bot_token="123:abc", telegram_chat_id="42"))
    assert notifier.enabled is True


def test_disabled_with_only_token():
    notifier = AlertNotifier(_settings(telegram_bot_token="123:abc"))
    assert notifier.enabled is False


def test_enabled_notify_sends_via_api(monkeypatch):
    sent = {}

    class _FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return b"{}"

    def _fake_urlopen(request, timeout):
        sent["url"] = request.full_url
        sent["body"] = request.data
        return _FakeResponse()

    monkeypatch.setattr("app.core.alerts.urllib.request.urlopen", _fake_urlopen)

    notifier = AlertNotifier(_settings(telegram_bot_token="123:abc", telegram_chat_id="42"))
    notifier._send("тестовое сообщение")

    assert sent["url"] == "https://api.telegram.org/bot123:abc/sendMessage"
    assert b"42" in sent["body"]
