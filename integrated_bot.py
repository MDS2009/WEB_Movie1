#!/usr/bin/env python
"""
Интегрированный Telegram бот для RV КИНО
Работает синхронно с Django сайтом через webhook
"""
import os
import sys
import django
import json
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rvkino.settings')
django.setup()

from django.conf import settings
from users.telegram_bot import telegram_bot
from users.models import TelegramVerificationToken

logger = logging.getLogger(__name__)

class IntegratedTelegramBot:
    def __init__(self):
        self.bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
        if not self.bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN не настроен в settings")
        
        self.application = Application.builder().token(self.bot_token).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        """Настройка обработчиков команд и сообщений"""
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("reset_password", self.reset_password_command))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
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
            "Готовы начать? Просто отправьте мне 6-значный код с сайта! 🚀"
        )
        
        await update.message.reply_text(welcome_text, parse_mode='Markdown')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /help"""
        help_text = (
            "🤖 *RV КИНО Бот - Справка*\n\n"
            "*📋 Доступные команды:*\n"
            "/start - Начать работу и получить инструкцию\n"
            "/help - Показать это справочное сообщение\n"
            "/reset_password - Сбросить пароль аккаунта\n\n"
            "*🔧 Как я работаю:*\n"
            "1. Получите 6-значный код на сайте RV КИНО для подключения Telegram\n"
            "2. Отправьте этот код мне\n"
            "3. Я подтвержу получение кода\n"
            "4. Завершите подключение на сайте\n\n"
            "*🔐 Сброс пароля:*\n"
            "1. Используйте команду /reset_password\n"
            "2. Следуйте инструкциям на сайте\n"
            "3. Отправьте 8-значный код верификации\n"
            "4. Получите ссылку для сброса пароля\n\n"
            "*⚠️ Важно:*\n"
            "• Коды действительны 15 минут\n"
            "• Каждый код уникален для вашего аккаунта\n"
            "• Один код можно использовать только один раз\n"
            "• У вас есть 3 попытки ввода кода сброса пароля\n\n"
            "*🎬 О RV КИНО:*\n"
            "Платформа для просмотра фильмов и создания сообществ по интересам."
        )
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def reset_password_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /reset_password"""
        reset_text = (
            "🔐 *Сброс пароля - RV КИНО*\n\n"
            "Чтобы сбросить пароль, выполните следующие шаги:\n\n"
            "1️⃣ Зайдите на сайт RV КИНО\n"
            "2️⃣ На странице входа нажмите \"Забыли пароль?\"\n"
            "3️⃣ Введите ваш номер телефона\n"
            "4️⃣ Скопируйте 8-значный код верификации с сайта\n"
            "5️⃣ Отправьте этот код мне в этот чат\n\n"
            "📋 *Важно:*\n"
            "• Код действителен 15 минут\n"
            "• Код состоит из 8 символов (буквы и цифры)\n"
            "• У вас есть 3 попытки ввода\n\n"
            "Готовы? Отправьте мне 8-значный код! 🚀"
        )
        
        await update.message.reply_text(reset_text, parse_mode='Markdown')
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка обычных сообщений"""
        text = update.message.text.strip()
        chat_id = str(update.message.chat.id)
        
        # Если пользователь отправляет 8-значный код верификации сброса пароля
        if len(text) == 8 and text.isalnum():
            await self.handle_password_reset_verification(update, chat_id, text)
        # Если пользователь отправляет 6-значный код
        elif text.isdigit() and len(text) == 6:
            # Используем Django сервис для проверки кода
            result = telegram_bot.verify_code(chat_id, text)
            
            await update.message.reply_text(result['message'], parse_mode='HTML')
            
            # Логируем результат
            if result['success']:
                logger.info(f"Код {text} успешно подтвержден для chat_id: {chat_id}")
            else:
                logger.warning(f"Неверный код {text} от chat_id: {chat_id}")
        else:
            # Ответ на другие сообщения
            help_text = (
                "🤖 *RV КИНО Бот*\n\n"
                "Я помогу вам подключить Telegram к вашему аккаунту на сайте RV КИНО.\n\n"
                "*🔧 Что делать:*\n"
                "1. Зайдите на сайт RV КИНО\n"
                "2. В профиле нажмите \"Подключить Telegram\"\n"
                "3. Отправьте мне 6-значный код с сайта\n\n"
                "*� Сброс пароля:*\n"
                "Используйте команду /reset_password\n\n"
                "*�📋 Команды:*\n"
                "/start - Начать работу\n"
                "/help - Показать справку\n"
                "/reset_password - Сбросить пароль\n\n"
                "Готов к работе! Отправьте мне код с сайта 🚀"
            )
            
            await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def handle_password_reset_verification(self, update: Update, chat_id: str, code: str):
        """Обработка 8-значного кода верификации сброса пароля"""
        try:
            from users.models import PasswordResetVerification, PasswordResetToken
            
            # Ищем активную верификацию по коду
            verification = PasswordResetVerification.objects.filter(
                verification_code=code.upper(),
                verified_at__isnull=True
            ).select_related('user').first()
            
            if not verification:
                await update.message.reply_text(
                    "❌ *Неверный код верификации*\n\n"
                    "Проверьте правильность кода и попробуйте еще раз.\n"
                    "Код должен состоять из 8 символов.",
                    parse_mode='Markdown'
                )
                return
            
            if verification.is_expired:
                await update.message.reply_text(
                    "⏰ *Срок действия кода истек*\n\n"
                    "Запросите новый код на сайте RV КИНО.\n"
                    "Код действителен 15 минут.",
                    parse_mode='Markdown'
                )
                return
            
            if not verification.can_attempt:
                await update.message.reply_text(
                    "🚫 *Превышено количество попыток*\n\n"
                    "Вы исчерпали лимит попыток ввода кода.\n\n"
                    "👨‍💻 *Нужна помощь?*\n"
                    "Свяжитесь со специалистом поддержки на сайте RV КИНО.",
                    parse_mode='Markdown'
                )
                return
            
            # Проверяем соответствие chat_id
            user_profile = verification.user.profile
            if user_profile.telegram_chat_id != chat_id:
                verification.increment_failed_attempts()
                remaining_attempts = verification.max_attempts - verification.failed_attempts
                
                if remaining_attempts > 0:
                    await update.message.reply_text(
                        f"❌ *Неверный пользователь*\n\n"
                        f"Этот код привязан к другому аккаунту.\n\n"
                        f"🔄 Осталось попыток: {remaining_attempts}",
                        parse_mode='Markdown'
                    )
                else:
                    await update.message.reply_text(
                        "🚫 *Превышено количество попыток*\n\n"
                        "Вы исчерпали лимит попыток ввода кода.\n\n"
                        "👨‍💻 *Нужна помощь?*\n"
                        "Свяжитесь со специалистом поддержки на сайте RV КИНО.",
                        parse_mode='Markdown'
                    )
                return
            
            # Все проверки пройдены - создаем токен сброса пароля
            reset_token = PasswordResetToken.objects.create(user=verification.user)
            
            # Отмечаем верификацию как успешную
            verification.mark_verified(reset_token.token)
            
            # Создаем ссылку для сброса пароля
            reset_url = f"http://127.0.0.1:8000/accounts/password-reset/confirm/{reset_token.token}/"
            
            success_text = (
                f"✅ *Верификация успешна!*\n\n"
                f"🔗 *Ваша ссылка для сброса пароля:*\n"
                f"{reset_url}\n\n"
                f"⏰ Ссылка действительна 15 минут.\n"
                f"🔒 Никому не передавайте эту ссылку!\n\n"
                f"Нажмите на ссылку, чтобы установить новый пароль."
            )
            
            await update.message.reply_text(success_text, parse_mode='Markdown')
            logger.info(f"Успешная верификация сброса пароля для chat_id: {chat_id}")
            
        except Exception as e:
            logger.error(f"Ошибка при обработке кода сброса пароля: {e}")
            await update.message.reply_text(
                "⚠️ *Произошла ошибка*\n\n"
                "Попробуйте еще раз или обратитесь в поддержку.",
                parse_mode='Markdown'
            )
    
    async def post_init(self, application: Application) -> None:
        """Инициализация после запуска"""
        bot_info = await application.bot.get_me()
        logger.info(f"🤖 Бот запущен: {bot_info.first_name} (@{bot_info.username})")
        print(f"🤖 Бот запущен: {bot_info.first_name} (@{bot_info.username})")
    
    def run_webhook(self, webhook_url: str = None):
        """Запуск бота в режиме webhook"""
        if not webhook_url:
            webhook_url = f"{getattr(settings, 'SITE_URL', 'https://rvkino.ru')}/accounts/telegram/webhook/"
        
        logger.info(f"🚀 Запуск бота в режиме webhook: {webhook_url}")
        print(f"🚀 Запуск бота в режиме webhook: {webhook_url}")
        
        # Устанавливаем webhook
        self.application.run_webhook(
            listen="0.0.0.0",
            port=8443,
            url_path="accounts/telegram/webhook/",
            webhook_url=webhook_url,
            secret_token=getattr(settings, 'TELEGRAM_WEBHOOK_SECRET', None)
        )
    
    def run_polling(self):
        """Запуск бота в режиме polling (для разработки)"""
        logger.info("📡 Запуск бота в режиме polling")
        print("📡 Запуск бота в режиме polling")
        print("⚠️  Не закрывайте это окно - бот будет работать")
        print("🛑 Для остановки нажмите Ctrl+C")
        
        self.application.run_polling()

def main():
    """Основная функция запуска бота"""
    try:
        bot = IntegratedTelegramBot()
        
        print("=" * 50)
        print("🎬 RV КИНО - Интегрированный запуск бота")
        print("=" * 50)
        
        # Проверяем режим запуска
        mode = os.environ.get('BOT_MODE', 'polling').lower()
        
        if mode == 'webhook':
            webhook_url = os.environ.get('WEBHOOK_URL')
            bot.run_webhook(webhook_url)
        else:
            bot.run_polling()
            
    except KeyboardInterrupt:
        print("\n🛑 Остановка бота...")
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        logger.error(f"Ошибка запуска бота: {e}")

if __name__ == "__main__":
    main()
