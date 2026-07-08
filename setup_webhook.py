#!/usr/bin/env python
"""
Скрипт для настройки webhook Telegram бота
Usage: python setup_webhook.py <your_webhook_url>
Example: python setup_webhook.py https://yourdomain.com/accounts/telegram/webhook/
"""
import os
import sys
import django
import asyncio

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rvkino.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.conf import settings
from telegram import Bot
from telegram.error import TelegramError

async def setup_webhook_async(webhook_url: str):
    """Настройка webhook для бота (async версия)"""
    bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
    
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN не найден в настройках")
        print("   Проверьте .env файл")
        return False
    
    try:
        bot = Bot(token=bot_token)
        
        # Удаляем старый webhook
        print("🧹 Удаляем старый webhook...")
        await bot.delete_webhook()
        
        # Устанавливаем новый webhook
        print(f"🌐 Устанавливаем webhook: {webhook_url}")
        result = await bot.set_webhook(url=webhook_url)
        
        if result:
            # Проверяем информацию о webhook
            webhook_info = await bot.get_webhook_info()
            print(f"✅ Webhook успешно настроен!")
            print(f"   URL: {webhook_info.url}")
            print(f"   Ожидает обновлений: {webhook_info.pending_update_count}")
            print(f"   Последняя ошибка: {webhook_info.last_error_message or 'нет'}")
            return True
        else:
            print("❌ Не удалось установить webhook")
            return False
            
    except TelegramError as e:
        print(f"❌ Ошибка Telegram API: {e}")
        return False
    except Exception as e:
        print(f"❌ Неизвестная ошибка: {e}")
        return False

async def delete_webhook_async():
    """Удаление webhook (async версия)"""
    bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
    
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN не найден")
        return False
    
    try:
        bot = Bot(token=bot_token)
        await bot.delete_webhook()
        print("✅ Webhook удален")
        return True
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

async def get_webhook_info_async():
    """Получить информацию о webhook (async версия)"""
    bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
    
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN не найден")
        return
    
    try:
        bot = Bot(token=bot_token)
        info = await bot.get_webhook_info()
        
        print("📊 Информация о webhook:")
        print(f"   URL: {info.url or 'не настроен'}")
        print(f"   Ожидает обновлений: {info.pending_update_count}")
        print(f"   Макс соединений: {info.max_connections}")
        
        if info.last_error_date:
            print(f"   Последняя ошибка: {info.last_error_message}")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def setup_webhook(webhook_url: str):
    """Синхронная обертка для setup_webhook_async"""
    return asyncio.run(setup_webhook_async(webhook_url))

def delete_webhook():
    """Синхронная обертка для delete_webhook_async"""
    return asyncio.run(delete_webhook_async())

def get_webhook_info():
    """Синхронная обертка для get_webhook_info_async"""
    asyncio.run(get_webhook_info_async())

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Настройка Telegram webhook')
    parser.add_argument('action', choices=['set', 'delete', 'info'], 
                       help='Действие: set (установить), delete (удалить), info (информация)')
    parser.add_argument('--url', type=str, help='URL для webhook (требуется для set)')
    
    args = parser.parse_args()
    
    if args.action == 'set':
        if not args.url:
            # Пробуем получить URL из настроек
            site_url = getattr(settings, 'SITE_URL', None)
            if site_url:
                url = f"{site_url}/accounts/telegram/webhook/"
                print(f"🌐 Используем URL из настроек: {url}")
            else:
                print("❌ Укажите --url или настройте SITE_URL в settings")
                sys.exit(1)
        else:
            url = args.url
        
        success = setup_webhook(url)
        sys.exit(0 if success else 1)
        
    elif args.action == 'delete':
        success = delete_webhook()
        sys.exit(0 if success else 1)
        
    elif args.action == 'info':
        get_webhook_info()

if __name__ == "__main__":
    main()
