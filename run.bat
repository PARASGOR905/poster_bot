@echo off
echo Starting OTT Content Scraper Bot...
echo.
echo Before running the bot, make sure you have:
echo 1. Set your BOT_TOKEN in the .env file
echo    (Get it from @BotFather on Telegram)
echo 2. Installed required packages: pip install -r requirements.txt
echo.
echo Press any key to continue...
pause >nul
echo.
python ott_scraper_bot.py
if errorlevel 1 (
    echo.
    echo Failed to start the bot. Please check:
    echo 1. That Python is installed and in your PATH
    echo 2. That all required packages are installed
    echo 3. That your BOT_TOKEN is set in the .env file
    echo.
    pause
)