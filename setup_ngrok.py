#!/usr/bin/env python
"""
Скрипт для настройки ngrok для локального тестирования Telegram бота
"""
import subprocess
import requests
import time
import os
import sys

def install_ngrok():
    """Проверка и установка ngrok"""
    try:
        result = subprocess.run(['ngrok', 'version'], capture_output=True, text=True)
        print("✅ ngrok уже установлен")
        return True
    except FileNotFoundError:
        print("❌ ngrok не найден")
        print("📥 Скачайте ngrok с https://ngrok.com/download")
        print("📋 Или установите через:")
        print("   Windows: chocolatey install ngrok")
        print("   MacOS: brew install ngrok")
        return False

def start_ngrok_tunnel():
    """Запуск ngrok туннеля"""
    try:
        # Запускаем ngrok для порта 8000
        process = subprocess.Popen([
            'ngrok', 'http', '8000', '--log=stdout'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        print("🚀 Запускаем ngrok туннель...")
        time.sleep(3)  # Даем время на запуск
        
        # Получаем публичный URL
        try:
            response = requests.get('http://127.0.0.1:4040/api/tunnels')
            tunnels = response.json()
            public_url = tunnels['tunnels'][0]['public_url']
            print(f"🔗 Публичный URL: {public_url}")
            return public_url, process
        except Exception as e:
            print(f"❌ Ошибка получения URL: {e}")
            process.terminate()
            return None, None
            
    except Exception as e:
        print(f"❌ Ошибка запуска ngrok: {e}")
        return None, None

def setup_telegram_webhook(webhook_url):
    """Настройка webhook для Telegram бота"""
    try:
        import django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rvkino.settings')
        django.setup()
        
        from users.telegram_bot import telegram_bot
        
        webhook_full_url = f"{webhook_url}/accounts/telegram/webhook/"
        print(f"🔧 Настраиваем webhook: {webhook_full_url}")
        
        # Устанавливаем webhook
        result = telegram_bot.bot.set_webhook(url=webhook_full_url)
        
        if result:
            print("✅ Webhook успешно настроен")
            print(f"🌐 Бот доступен по: {webhook_full_url}")
            return True
        else:
            print("❌ Ошибка настройки webhook")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def main():
    print("=" * 50)
    print("🎬 RV КИНО - Настройка ngrok для Telegram бота")
    print("=" * 50)
    
    # 1. Проверяем ngrok
    if not install_ngrok():
        input("\nНажмите Enter после установки ngrok...")
        if not install_ngrok():
            print("❌ ngrok не установлен. Выход.")
            return
    
    # 2. Запускаем ngrok
    public_url, ngrok_process = start_ngrok_tunnel()
    if not public_url:
        print("❌ Не удалось запустить ngrok")
        return
    
    # 3. Настраиваем webhook
    if setup_telegram_webhook(public_url):
        print("\n✅ Все готово для тестирования!")
        print("📋 Теперь вы можете:")
        print("1. Запустить Django сервер: python manage.py runserver")
        print("2. Отправить сообщения боту в Telegram")
        print("3. Тестировать подключение на сайте")
        print("\n⚠️  Не закрывайте это окно - ngrok будет работать")
        print("🛑 Для остановки нажмите Ctrl+C")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Остановка ngrok...")
            ngrok_process.terminate()
            print("✅ Готово")
    else:
        print("❌ Не удалось настроить webhook")
        if ngrok_process:
            ngrok_process.terminate()

if __name__ == "__main__":
    main()
