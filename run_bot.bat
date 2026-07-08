@echo off
REM Запуск Telegram бота для RV КИНО через Django management command
REM Usage: run_bot.bat [polling|webhook]

cd /d "%~dp0"

echo ==========================================
echo    RV КИНО - Telegram Bot Launcherecho ==========================================

if "%~1"=="" (
    echo Запуск в режиме polling (для разработки)...
    python manage.py run_telegram_bot --mode polling
) else if "%~1"=="webhook" (
    echo Запуск в режиме webhook (для production)...
    python manage.py run_telegram_bot --mode webhook --webhook-url %~2
) else (
    echo Запуск в режиме: %~1
    python manage.py run_telegram_bot --mode %~1
)

pause
