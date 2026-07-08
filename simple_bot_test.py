#!/usr/bin/env python
"""
Простой тест Telegram бота без Django
"""
import asyncio
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# Получаем токен из .env файла
def get_bot_token():
    try:
        with open('.env', 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('TELEGRAM_BOT_TOKEN='):
                    return line.split('=', 1)[1].strip()
    except FileNotFoundError:
        pass
    return None

# Тестовая база данных токенов (в памяти)
test_tokens = {}

async def start_command(update: Update, context):
    """Обработка команды /start"""
    welcome_text = (
        "🎬 *Добро пожаловать в RV КИНО бот!*\n\n"
        "Я помогу вам подключить Telegram к вашему аккаунту на сайте RV КИНО.\n\n"
        "*📋 Как подключить Telegram:*\n"
        "1️⃣ Зайдите на сайт RV КИНО и авторизуйтесь\n"
        "2️⃣ Перейдите в свой профиль\n"
        "3️⃣ Нажмите кнопку *\"Подключить Telegram\"*\n"
        "4️⃣ Скопируйте 6-значный код с сайта\n"
        "5️⃣ Отправьте этот код мне в этот чат\n"
        "6️⃣ Введите тот же код в форму на сайте для завершения\n\n"
        "*⚡ Что вы получите после подключения:*\n"
        "• Уведомления о новых фильмах\n"
        "• Напоминания о просмотренных фильмах\n"
        "• Информацию об обновлениях в ваших сообществах\n"
        "• Быстрый доступ к вашему профилю\n\n"
        "*❓ Нужна помощь?*\n"
        "Если у вас возникли вопросы, обратитесь в поддержку на сайте RV КИНО.\n\n"
        "Готовы начать? Просто отправьте мне 6-значный код с сайта! 🚀"
    )
    
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def help_command(update: Update, context):
    """Обработка команды /help"""
    help_text = (
        "🤖 *RV КИНО Бот - Справка*\n\n"
        "*📋 Доступные команды:*\n"
        "/start - Начать работу и получить инструкцию\n"
        "/help - Показать это справочное сообщение\n\n"
        "*🔧 Как я работаю:*\n"
        "1. Получите 6-значный код на сайте RV КИНО\n"
        "2. Отправьте этот код мне\n"
        "3. Я подтвержу получение кода\n"
        "4. Завершите подключение на сайте\n\n"
        "*⚠️ Важно:*\n"
        "• Код действителен 15 минут\n"
        "• Каждый код уникален для вашего аккаунта\n"
        "• Один код можно использовать только один раз\n\n"
        "*🎬 О RV КИНО:*\n"
        "Платформа для просмотра фильмов и создания сообществ по интересам.\n\n"
        "*❓ Нужна дополнительная помощь?*\n"
        "Обратитесь в поддержку на сайте RV КИНО."
    )
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def handle_message(update: Update, context):
    """Обработка обычных сообщений"""
    text = update.message.text.strip()
    chat_id = str(update.message.chat.id)
    
    # Если пользователь отправляет 6-значный код
    if text.isdigit() and len(text) == 6:
        # Имитируем проверку кода
        if text in test_tokens:
            user_info = test_tokens[text]
            result = {
                'success': True,
                'message': f'✅ Код принят! Теперь {user_info["username"]} может завершить подключение на сайте.',
                'user_info': user_info
            }
            # Сохраняем chat_id
            test_tokens[text]['chat_id'] = chat_id
        else:
            result = {
                'success': False,
                'message': '❌ Неверный код. Проверьте правильность кода и попробуйте еще раз.'
            }
        
        await update.message.reply_text(result['message'], parse_mode='HTML')
    else:
        # Ответ на другие сообщения
        help_text = (
            "🤖 *RV КИНО Бот*\n\n"
            "Я помогу вам подключить Telegram к вашему аккаунту на сайте RV КИНО.\n\n"
            "*🔧 Что делать:*\n"
            "1. Зайдите на сайт RV КИНО\n"
            "2. В профиле нажмите \"Подключить Telegram\"\n"
            "3. Отправьте мне 6-значный код с сайта\n\n"
            "*📋 Команды:*\n"
            "/start - Начать работу\n"
            "/help - Показать справку\n\n"
            "Готов к работе! Отправьте мне код с сайта 🚀"
        )
        
        await update.message.reply_text(help_text, parse_mode='Markdown')

async def add_test_code(update: Update, context):
    """Добавить тестовый код (для разработки)"""
    if len(context.args) >= 2:
        code = context.args[0]
        username = ' '.join(context.args[1:])
        test_tokens[code] = {
            'username': username,
            'email': 'test@example.com'
        }
        await update.message.reply_text(f"✅ Добавлен тестовый код: {code} для пользователя: {username}")
    else:
        await update.message.reply_text("❌ Использование: /addcode код имя_пользователя")

async def main():
    """Основная функция запуска бота"""
    bot_token = get_bot_token()
    if not bot_token:
        print("❌ Токен бота не найден в .env файле")
        print("📋 Убедитесь, что в .env есть строка:")
        print("   TELEGRAM_BOT_TOKEN=ваш_токен")
        return
    
    try:
        # Создаем приложение
        application = Application.builder().token(bot_token).build()
        
        # Добавляем обработчики
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("addcode", add_test_code))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        # Получаем информацию о боте
        bot_info = await application.bot.get_me()
        print(f"🤖 Запускаем бота: {bot_info.first_name} (@{bot_info.username})")
        print("📡 Бот работает в режиме polling")
        print("⚠️  Не закрывайте это окно - бот будет работать")
        print("🛑 Для остановки нажмите Ctrl+C")
        print("🔧 Для добавления тестового кода: /addcode 123456 TestUser")
        
        # Запускаем бота
        print("🚀 Бот запущен и готов к работе!")
        await application.run_polling()
        
    except KeyboardInterrupt:
        print("\n🛑 Остановка бота...")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    print("=" * 50)
    print("🎬 RV КИНО - Простой тест бота")
    print("=" * 50)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n✅ Работа завершена")
