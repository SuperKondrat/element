"""Алерты об ошибках в Telegram.

Пока в .env не заданы TELEGRAM_BOT_TOKEN/TELEGRAM_CHAT_ID, это заглушка —
события только логируются. Как только секреты появятся, отправка в Telegram
Bot API включится сама, без изменений в вызывающем коде (см.
core/errors.py и api/rpc/dispatcher.py — оба используют get_alert_notifier()).
"""

import json
import logging
import threading
import urllib.error
import urllib.request
from functools import lru_cache

from app.config import Settings, get_settings

logger = logging.getLogger(__name__)

_TELEGRAM_API_URL = "https://api.telegram.org/bot{token}/sendMessage"
_REQUEST_TIMEOUT_SECONDS = 5


class AlertNotifier:
    def __init__(self, settings: Settings) -> None:
        self._token = settings.telegram_bot_token
        self._chat_id = settings.telegram_chat_id

    @property
    def enabled(self) -> bool:
        return bool(self._token and self._chat_id)

    def notify_error(self, source: str, detail: str) -> None:
        message = f"[Element] Ошибка в {source}\n{detail}"
        if not self.enabled:
            logger.info("Telegram-алерт (бот не настроен, заглушка): %s", message)
            return
        # Реальная отправка — в отдельном потоке, чтобы не блокировать обработку запроса
        # синхронным HTTP-вызовом.
        threading.Thread(target=self._send, args=(message,), daemon=True).start()

    def _send(self, message: str) -> None:
        url = _TELEGRAM_API_URL.format(token=self._token)
        payload = json.dumps({"chat_id": self._chat_id, "text": message}).encode("utf-8")
        request = urllib.request.Request(
            url, data=payload, headers={"Content-Type": "application/json"}, method="POST"
        )
        try:
            with urllib.request.urlopen(request, timeout=_REQUEST_TIMEOUT_SECONDS) as response:
                response.read()
        except (urllib.error.URLError, OSError):
            logger.exception("Не удалось отправить Telegram-алерт")


@lru_cache
def get_alert_notifier() -> AlertNotifier:
    return AlertNotifier(get_settings())
