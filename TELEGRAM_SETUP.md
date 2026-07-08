# Инструкция по настройке Telegram бота для RV КИНО

## 1. Создание Telegram бота

1. Найдите в Telegram **@BotFather**
2. Отправьте команду `/newbot`
3. Следуйте инструкциям:
   - Имя бота: `RV КИНО Bot`
   - Username бота: `rvkino_bot` (или другой уникальный)
4. Сохраните **токен бота**, который вам пришлет BotFather

## 2. Настройка проекта

1. Создайте файл `.env` в корне проекта
2. Скопируйте содержимое из `.env example`
3. Добавьте настройки Telegram:
   ```
   TELEGRAM_BOT_TOKEN=ваш-токен-от-бота
   TELEGRAM_BOT_USERNAME=@ваш_username_бота
   SITE_URL=https://yourdomain.com  # Для production
   ```

## 3. Установка зависимостей

```bash
pip install python-telegram-bot==21.3
```

## 4. Способы запуска бота (СИНХРОННО с сайтом)

### Вариант A: Django Management Command (РЕКОМЕНДУЕТСЯ)

**Для разработки (polling):**
```bash
python manage.py run_telegram_bot --mode polling
```

**Для production (webhook):**
```bash
python manage.py run_telegram_bot --mode webhook --webhook-url https://yourdomain.com/accounts/telegram/webhook/
```

**Или используйте bat файл (Windows):**
```bash
run_bot.bat polling
```

### Вариант B: Автономный интегрированный бот

```bash
python integrated_bot.py
```

### Вариант C: Webhook endpoint (без постоянного процесса)

Настройте webhook у Telegram:
```bash
python setup_webhook.py set --url https://yourdomain.com/accounts/telegram/webhook/
```

Проверьте статус:
```bash
python setup_webhook.py info
```

Удалите webhook:
```bash
python setup_webhook.py delete
```

## 5. Как работает интеграция

### Архитектура:
```
Пользователь → Telegram API → Webhook URL → Django View → Обработка → Ответ
```

Бот теперь работает **синхронно с сайтом**:
- Один процесс (Django)
- Одна база данных
- Shared models через Django ORM

## 6. Структура файлов

```
Web_movie1/
├── integrated_bot.py              # Автономный бот с Django
├── setup_webhook.py               # Скрипт настройки webhook
├── run_bot.bat                    # Windows launcher
├── users/
│   ├── telegram_bot.py            # Django сервис
│   ├── telegram_views.py          # Webhook endpoint
│   └── management/
│       └── commands/
│           └── run_telegram_bot.py  # Django command
```

## 7. Тестирование

1. Запустите Django: `python manage.py runserver`
2. Запустите бота: `python manage.py run_telegram_bot --mode polling`
3. Откройте сайт, зайдите в профиль
4. Нажмите "Подключить Telegram", получите код
5. В Telegram найдите бота, отправьте код
6. Подтвердите на сайте

## 8. Примечания

- **Production**: Используйте webhook (не polling)
- Webhook endpoint: `/accounts/telegram/webhook/`
- Коды действуют 15 минут
- Бот использует Django ORM напрямую
