#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rvkino.settings')
django.setup()

from django.conf import settings
from users.telegram_bot import telegram_bot

print("=== Проверка настроек Telegram бота ===")
print(f"TELEGRAM_BOT_TOKEN: {'***' + settings.TELEGRAM_BOT_TOKEN[-4:] if settings.TELEGRAM_BOT_TOKEN else 'None'}")
print(f"TELEGRAM_BOT_USERNAME: {settings.TELEGRAM_BOT_USERNAME}")
print(f"Бот настроен: {telegram_bot.is_configured()}")

# Попробуем отправить тестовое сообщение
test_chat_id = "5668956661"  # chat_id пользователя Test11
print(f"\n=== Попытка отправить тестовое сообщение в {test_chat_id} ===")

try:
    result = telegram_bot.send_verification_code(test_chat_id, "123456", "тестовый")
    print(f"Результат отправки: {result}")
except Exception as e:
    print(f"Ошибка при отправке: {e}")
