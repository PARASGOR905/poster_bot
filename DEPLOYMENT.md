# Deployment Guide

This guide explains how to deploy your OTT Poster Scraper Bot on Railway.app for 24/7 operation.

## Prerequisites

- A GitHub account
- A Railway.app account
- Your bot token from @BotFather

## Deployment Steps

### 1. Prepare Your Repository

Your project structure should look like this:

```
project/
│── ott_scraper_bot.py
│── requirements.txt
│── Procfile
│── .gitignore
│── run.bat   (optional, local use only)
└── DEPLOYMENT.md (this file)
```

### 2. Push Code to GitHub

```bash
git init
git add .
git commit -m "OTT Poster Scraper Bot"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
git push -u origin main
```

> **Important**: Make sure `.env` is in `.gitignore` and not uploaded to GitHub for security.

### 3. Deploy on Railway

1. Go to [https://railway.app](https://railway.app)
2. Sign in with your GitHub account
3. Click "New Project"
4. Select "Deploy from GitHub Repo"
5. Choose your repository
6. Railway will automatically detect it's a Python project

### 4. Configure Environment Variables

In Railway, go to **Variables** and add:

```
BOT_TOKEN = your_real_bot_token
OWNER_IDS = 6940979626
```

> Add any other sensitive information as environment variables, not in the code.

### 5. Start the Bot

Railway will automatically run:
```
python ott_scraper_bot.py
```

You'll see logs indicating the bot is running:
```
Bot started...
Application running...
```

## Alternative: Render.com

If you prefer Render.com:

1. Go to [https://render.com](https://render.com)
2. Create a new Web Service
3. Connect to your GitHub repository
4. Set Build Command:
   ```
   pip install -r requirements.txt
   ```
5. Set Start Command:
   ```
   python ott_scraper_bot.py
   ```
6. Add Environment Variables
7. Deploy

## Important Notes

- **Never hardcode sensitive tokens** in the source code
- **Always use environment variables** for secrets
- The bot uses **polling method** which works well for Railway deployment
- Railway provides free tier with auto-restart capabilities
- Keep your bot token secure and never share it publicly

## Troubleshooting

### Bot exits immediately
- Check if BOT_TOKEN is correctly set in environment variables

### ModuleNotFoundError
- Verify requirements.txt has all necessary dependencies

### Bot starts but doesn't respond
- Confirm the bot token is correct
- Ensure no webhook is set (use @BotFather to check)

## Recommendation

Railway.app with polling method is the best setup for this bot, providing reliable 24/7 operation on the free tier.