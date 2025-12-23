# OTT Content Scraper Bot

A Telegram bot that scrapes high-quality posters and content information from 13+ OTT platforms.

## Features

- 🖼️ 4K Ultra HD poster quality
- 📋 Detailed content information
- ⚡ Fast and reliable performance
- 🌐 Multi-platform support (26+ services)
- 🎯 Supports major OTT platforms:
  - Amazon Prime Video
  - Hulu
  - Z5
  - Airtel Xstream
  - SunNext, Stage, Adda, WeTV
  - Plex, IQIYI, Aha, Shemaroo
  - Apple TV
  - BookMyShow (BMS)
  - HubCloud, VCloud, HubCDN
  - DriveLeech, HubDrive, Neo
  - GDRex, PixelCDN, ExtraFlix
  - ExtraLink, LuxDrive, GDFlix

## Setup Instructions

1. **Get API Credentials:**
   - Get your `BOT_TOKEN` from [@BotFather](https://t.me/BotFather) on Telegram

2. **Configure Environment Variables:**
   - Edit the `.env` file and set your credentials:
     ```
     BOT_TOKEN=your_bot_token_here
     # Optional: Set owner IDs (comma-separated)
     OWNER_IDS=your_user_id_here
     ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Bot:**
   ```bash
   python ott_scraper_bot.py
   ```
   Or double-click `run.bat` on Windows.

## Usage

1. Start the bot by sending `/start`
2. Use platform-specific commands with URLs:
   - `/prime https://www.primevideo.com/detail/...`
   - `/z5 https://www.zee5.com/...`
   - `/hulu https://www.hulu.com/...`
   - And more...

## Commands

- `/start` - Show welcome message
- `/help` - Detailed instructions
- `/about` - Information about the bot
- `/stats` - Usage statistics
- `/settings` - Configure preferences
- `/quality` - Change image quality
- `/premium` - Check premium membership
- `/mediainfo` - Get media info from video URL

## Supported Platforms

- Amazon Prime Video (`/prime`)
- Hulu (`/hulu`)
- Z5 (`/z5`)
- Airtel Xstream (`/airtel`)
- SunNext (`/sunnext`)
- Stage (`/stage`)
- Adda (`/adda`)
- WeTV (`/wetv`)
- Plex (`/plex`)
- IQIYI (`/iqiyi`)
- Aha (`/aha`)
- Shemaroo (`/shemaroo`)
- Apple TV (`/apple`)
- BookMyShow (`/bms`)

## Powered by

[@CineHub_Media](https://t.me/CineHub_Media)