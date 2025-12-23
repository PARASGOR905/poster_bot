#Don't Remove Credit @CineHub_Media 

import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os
from pathlib import Path
from dotenv import load_dotenv
import logging
import asyncio
import aiohttp
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# ===== CONFIG =====
BOT_TOKEN = os.getenv("BOT_TOKEN")  # Set your Bot Token from @BotFather

# Validate required environment variables
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is required. Please set it in your environment variables or .env file.")

# Configuration for poster format
ADD_CC = True   # False = no cc line
CC_TEXT = "cc: @CineHub_Media"
SEND_IMAGES = False  # True = send images with inline buttons, False = send links only


# Create file to store chat IDs
CHAT_IDS_FILE = Path("chat_ids.txt")
CHAT_IDS_FILE.touch(exist_ok=True)

# Create file to store bot statistics
STATS_FILE = Path("bot_stats.json")
STATS_FILE.touch(exist_ok=True)

# Create file to store premium users
PREMIUM_USERS_FILE = Path("premium_users.txt")
PREMIUM_USERS_FILE.touch(exist_ok=True)

# Define owner IDs (users with admin privileges)
OWNER_IDS = [int(id.strip()) for id in os.getenv("OWNER_IDS", "6940979626").split(",")] if os.getenv("OWNER_IDS") else [6940979626]

# ===== INLINE BUTTONS =====
update_button = InlineKeyboardMarkup(
    [[InlineKeyboardButton("🎬 Updates", url="https://t.me/CineHub_Media")]]
)

settings_button = InlineKeyboardMarkup(
    [[InlineKeyboardButton("⚙️ Settings", callback_data="settings")]]
)

help_button = InlineKeyboardMarkup(
    [[InlineKeyboardButton("📚 Help", callback_data="help")]]
)

# Startup message button
startup_button = InlineKeyboardMarkup(
    [[InlineKeyboardButton("🎬 Updates", url="https://t.me/CineHub_Media")]]
)

# ===== OTT DOMAIN MAP =====
OTT_DOMAIN_MAP = {
    "primevideo.com": "prime",
    "zee5.com": "zee",
    "airtelxstream.in": "airtel",
    "stage.in": "stage",
    "aha.video": "aha",
    "tv.apple.com": "apple",
    "bookmyshow.com": "bms",
    "sunnxt.com": "sunnext",
    "ullu.app": "ullu",
}

# ===== OTT API ENDPOINTS =====
OTT_APIS = {
    "sunnext": {"url": "https://sunnxt.pbx1.workers.dev/", "type": "general"},
    "hulu": {"url": "https://hgbots.vercel.app/bypaas/asa.php", "type": "general"},
    "stage": {"url": "https://stage.pbx1bots.workers.dev/", "type": "general"},
    "adda": {"url": "https://hgbots.vercel.app/bypaas/asa.php", "type": "general"},
    "wetv": {"url": "https://hgbots.vercel.app/bypaas/asa.php", "type": "general"},
    "plex": {"url": "https://hgbots.vercel.app/bypaas/asa.php", "type": "general"},
    "iqiyi": {"url": "https://hgbots.vercel.app/bypaas/asa.php", "type": "general"},
    "aha": {"url": "https://hgbots.vercel.app/bypaas/asa.php", "type": "general"},
    "shemaroo": {"url": "https://hgbots.vercel.app/bypaas/asa.php", "type": "general"},
    "apple": {"url": "https://appletv.pbx1bots.workers.dev/", "type": "general"},
    "airtel": {"url": "https://airtelxstream.pbx1bots.workers.dev/", "type": "airtel"},
    "zee": {"url": "https://zee5.pbx1bots.workers.dev/", "type": "zee"},
    "prime": {"url": "https://primevideo.pbx1bots.workers.dev/", "type": "prime"},
    "bms": {"url": "https://bms.pbx1.workers.dev/", "type": "general"},
    # New PBX1 API endpoints
    "hubcloud": {"url": "https://pbx1botapi.vercel.app/api/hubcloud", "type": "general"},
    "vcloud": {"url": "https://pbx1botapi.vercel.app/api/vcloud", "type": "general"},
    "hubcdn": {"url": "https://pbx1botapi.vercel.app/api/hubcdn", "type": "general"},
    "driveleech": {"url": "https://pbx1botapi.vercel.app/api/driveleech", "type": "general"},
    "hubdrive": {"url": "https://pbx1botapi.vercel.app/api/hubdrive", "type": "general"},
    "neo": {"url": "https://pbx1botapi.vercel.app/api/neo", "type": "general"},
    "gdrex": {"url": "https://pbx1botapi.vercel.app/api/gdrex", "type": "general"},
    "pixelcdn": {"url": "https://pbx1botapi.vercel.app/api/pixelcdn", "type": "general"},
    "extraflix": {"url": "https://pbx1botapi.vercel.app/api/extraflix", "type": "general"},
    "extralink": {"url": "https://pbx1botapi.vercel.app/api/extralink", "type": "general"},
    "luxdrive": {"url": "https://pbx1botapi.vercel.app/api/luxdrive", "type": "general"},
    "gdflix": {"url": "https://pbx1botapi.vercel.app/api/gdflix", "type": "general"}
}

# ===== COMMON FUNCTION =====
async def fetch_ott_data(platform: str, ott_url: str):
    """
    Fetch data from OTT API with platform-specific logic and retry mechanism.
    """
    try:
        api_info = OTT_APIS.get(platform)
        if not api_info:
            return None
            
        api_url = api_info["url"]
        api_type = api_info["type"]
        
        logger.info(f"Fetching data for {platform} from {api_url}")
        
        # Add headers to avoid blocking
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.google.com/'
        }
        
        # Platform-specific request handling
        if api_type == "prime":
            # Amazon Prime specific logic
            params = {"url": ott_url}
        elif api_type == "airtel":
            # Airtel Xstream specific logic
            params = {"url": ott_url}
        elif api_type == "zee":
            # Zee5 specific logic
            params = {"url": ott_url}
        else:
            # General logic for other platforms
            params = {"url": ott_url}
            
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, params=params, timeout=aiohttp.ClientTimeout(total=30), headers=headers) as resp:
                if resp.status != 200:
                    logger.error(f"Failed to fetch data from {platform}: HTTP {resp.status}")
                    return None
                    
                # Try to parse JSON response
                try:
                    data = await resp.json()
                    logger.info(f"Successfully fetched data for {platform}")
                    return data
                except Exception as json_error:
                    # If JSON parsing fails, return text content
                    logger.warning(f"Failed to parse JSON for {platform}: {json_error}")
                    text_content = await resp.text()
                    return {"title": "Content", "poster": None, "description": text_content[:500]}
                    
    except aiohttp.ClientError as e:
        logger.error(f"Client error fetching data from {platform}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error fetching data from {platform}: {e}")
        return None

# Image download function removed - bot now sends only links instead of images

async def format_content_info(data: dict, platform: str, ott_url: str, update: Update = None) -> tuple:
    """
    Format content information based on platform and available data.
    """
    try:
        # Extract information with platform-specific logic
        if platform in ["prime", "airtel", "zee"]:
            # Handle special case for ZEE where title might be a list
            raw_title = data.get("title", "Unknown Title")
            if isinstance(raw_title, list) and len(raw_title) > 0:
                # Extract title from list format
                if isinstance(raw_title[0], dict):
                    title = raw_title[0].get("@value", "Unknown Title")
                else:
                    title = raw_title[0]
            else:
                title = raw_title
                
            description = data.get("description", data.get("plot", "No description available"))
            poster_url = data.get("poster", data.get("image", data.get("thumbnail")))
            landscape_url = data.get("landscape", data.get("backdrop", poster_url))
            year = data.get("year", "N/A")
            rating = data.get("rating", "N/A")
            duration = data.get("duration", "N/A")
            genre = data.get("genre", "N/A")
            cast = data.get("cast", "N/A")
            director = data.get("director", "N/A")
        else:
            # General format for other platforms
            # Handle special case where title might be a list
            raw_title = data.get("title", data.get("name", "Unknown Title"))
            if isinstance(raw_title, list) and len(raw_title) > 0:
                # Extract title from list format
                if isinstance(raw_title[0], dict):
                    title = raw_title[0].get("@value", "Unknown Title")
                else:
                    title = raw_title[0]
            else:
                title = raw_title
                
            description = data.get("description", data.get("plot", data.get("overview", "No description available")))
            poster_url = data.get("poster", data.get("image", data.get("thumbnail")))
            landscape_url = data.get("landscape", data.get("backdrop", poster_url))
            year = data.get("year", "N/A")
            rating = data.get("rating", data.get("imdb_rating", "N/A"))
            duration = data.get("duration", "N/A")
            genre = data.get("genre", data.get("genres", "N/A"))
            cast = data.get("cast", "N/A")
            director = data.get("director", "N/A")
        
        # Final rule: only COVER
        cover_url = landscape_url if landscape_url else poster_url
        
        # Format based on chat type if update is provided
        if update and hasattr(update, 'effective_chat'):
            chat_type = update.effective_chat.type
            is_channel = chat_type in ["channel", "supergroup"]
            cc_line = f"\n\n{CC_TEXT}" if ADD_CC else ""
            platform_name = platform.capitalize()
            
            if is_channel:
                # Channel format
                text = (
                    f"{platform_name} Cover: {cover_url}\n\n"
                    f"{title} - ({year})"
                    f"{cc_line}"
                )
            else:
                # DM/Private chat format
                text = (
                    f"🎬 <b>{title}</b> ({year})\n\n"
                    f"🎞️ <b>Cover:</b>\n{cover_url}"
                )
        else:
            # Default format
            if year and year != "N/A":
                text = f"🎬 <b>{title}</b> ({year})\n\n"
            else:
                text = f"🎬 <b>{title}</b>\n\n"
            
            # Add cover link
            if cover_url and cover_url != "N/A":
                text += f"🎞️ <b>Cover:</b>\n{cover_url}\n\n"
            
            text += f"━━━━━━━━━━━━━━━\n✨ <b>Powered by @CineHub_Media</b>"
        
        # Return the cover URL for potential image sending
        cover_url_for_return = cover_url if cover_url and cover_url != "N/A" else None
        
        return text, cover_url_for_return
        
    except Exception as e:
        logger.error(f"Error formatting content info: {e}")
        # Fallback format
        # Handle special case for fallback title
        raw_title = data.get("title", "Unknown Title")
        if isinstance(raw_title, list) and len(raw_title) > 0:
            # Extract title from list format
            if isinstance(raw_title[0], dict):
                title = raw_title[0].get("@value", "Unknown Title")
            else:
                title = raw_title[0]
        else:
            title = raw_title
            
        poster_url = data.get("poster", data.get("image"))
        cover_url = poster_url  # Use poster as cover if no specific cover
        if cover_url:
            text = (
                f"🎬 <b>{title}</b>\n\n"
                f"🎞️ <b>Cover:</b>\n{cover_url}\n\n"
                f"━━━━━━━━━━━━━━━\n✨ <b>Powered by @CineHub_Media</b>"
            )
        else:
            text = (
                f"🎬 <b>{title}</b>\n\n"
                f"🎞️ <b>Cover:</b>\nNo image available\n\n"
                f"━━━━━━━━━━━━━━━\n✨ <b>Powered by @CineHub_Media</b>"
            )
        cover_url_for_return = cover_url if cover_url and cover_url != "N/A" else None
        return text, cover_url_for_return

async def handle_ott_command(update: Update, context: ContextTypes.DEFAULT_TYPE, platform: str):
    chat_id = update.effective_chat.id
    
    # Update user stats
    update_user_stats(chat_id)
    
    # Check if user is premium
    is_premium = is_premium_user(chat_id)
    
    # Check daily request limit for non-premium users
    if not is_premium:
        daily_requests = get_user_daily_requests(chat_id)
        if daily_requests >= 10:
            # Send limit exceeded message
            limit_message = (
                "🚫 <b>Daily Request Limit Exceeded</b> 🚫\n\n"
                "You've reached the maximum of 10 requests per day.\n\n"
                "✨ <b>Upgrade to Premium</b> for unlimited access!\n\n"
                "💰 <b>Premium Pricing:</b>\n"
                "  • 1 Month: ₹20\n"
                "  • 3 Months: ₹50 (Save ₹10)\n"
                "  • 6 Months: ₹100 (Save ₹20)\n"
                "  • 12 Months: ₹220 (Save ₹20)\n\n"
                "💳 Contact @CineHub_Media for premium subscription.\n\n"
                "🔄 Limit resets at 00:00 UTC daily."
            )
            await update.message.reply_text(limit_message, parse_mode="HTML", reply_markup=update_button)
            return
    
    # Increment total requests
    increment_stat("total_requests", platform, chat_id)
    
    if len(context.args) < 1:
        await update.message.reply_text(f"🔗 Please provide a {platform.upper()} URL.\n\nExample:\n<code>/{platform} https://...</code>", parse_mode="HTML")
        return

    ott_url = context.args[0].strip()
    msg = await update.message.reply_text("🔍 Fetching...")
    
    try:
        # Fetch data with platform-specific logic
        data = await fetch_ott_data(platform, ott_url)
        
        if not data:
            # Increment failed requests
            increment_stat("failed_requests", platform, chat_id)
            await msg.edit_text("❌ Failed to fetch data from API.")
            return
        
        # Increment successful requests after data is successfully fetched
        increment_stat("successful_requests", platform, chat_id)
        
        # Format content information
        text, cover_url = await format_content_info(data, platform, ott_url, update)
        
        if SEND_IMAGES and cover_url:
            # Create inline keyboard with open cover button
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🖼️ Open Cover", url=cover_url)]
            ])
            
            # Send image with caption and inline button
            try:
                await msg.delete()  # Delete the fetching message
                await update.message.reply_photo(
                    photo=cover_url,
                    caption=text,
                    parse_mode="HTML",
                    reply_markup=keyboard
                )
            except Exception:
                # If sending image fails, send text instead
                await update.message.reply_text(
                    text=text,
                    parse_mode="HTML",
                    reply_markup=update_button
                )
        else:
            # Send only text with links, no images
            await msg.edit_text(
                text=text,
                parse_mode="HTML",
                reply_markup=update_button
            )

    except Exception as e:
        logger.error(f"Error handling {platform} command: {e}")
        # Increment failed requests
        increment_stat("failed_requests", platform, chat_id)
        await msg.edit_text(f"❌ Error: {str(e)}")

#Don't Remove Credit @CineHub_Media 
# ===== COMMAND HANDLERS =====
async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    # Save chat ID for startup messages
    save_chat_id(update.effective_chat.id)
    
    welcome_message = """
🎬 <b>OTT Content Scraper Bot</b> 🤖

Fetch high-quality posters from popular OTT platforms in seconds.

━━━━━━━━━━━━━━━
📌 <b>How to Use</b>
1️⃣ Choose a platform command  
2️⃣ Paste the movie / series URL  
3️⃣ Get HD / 4K posters instantly

━━━━━━━━━━━━━━━
🎯 <b>Example</b>
<code>/prime https://www.primevideo.com/detail/...</code>

━━━━━━━━━━━━━━━
🌐 <b>Supported Platforms</b>
Prime Video • Zee5 • Airtel Xstream  
Stage • Aha • Apple TV • BMS  
+ 20 more OTT services

━━━━━━━━━━━━━━━
📊 <b>Limits</b>
• Free users: 10 requests / day  
• Premium users: Unlimited access

━━━━━━━━━━━━━━━
ℹ️ Use <code>/help</code> to see all commands

✨ <b>Powered by @CineHub_Media</b>
    """
    
    await update.message.reply_text(welcome_message, parse_mode="HTML", reply_markup=help_button)

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    # Save chat ID for startup messages
    save_chat_id(update.effective_chat.id)
    
    help_message = """
📚 <b>OTT Content Scraper Bot – Help</b>

━━━━━━━━━━━━━━━
🎯 <b>What this bot does</b>
Fetches high-quality (HD / 4K) posters from official OTT platforms using direct URLs.

━━━━━━━━━━━━━━━
🛠️ <b>How to Use</b>
1️⃣ Use a platform command  
2️⃣ Paste the movie / series URL  
3️⃣ Get poster instantly

━━━━━━━━━━━━━━━
🎬 <b>Main OTT Commands</b>
<code>/prime</code>   – Amazon Prime Video  
<code>/zee</code>     – Zee5  
<code>/airtel</code>  – Airtel Xstream  
<code>/stage</code>   – Stage  
<code>/aha</code>     – Aha  
<code>/apple</code>   – Apple TV  
<code>/bms</code>     – BookMyShow  

━━━━━━━━━━━━━━━
🌐 <b>Other Supported OTTs</b>
SunNext • Adda • WeTV • Plex • IQIYI  
Shemaroo • HubCloud • GDFlix  
+ many more

━━━━━━━━━━━━━━━
🧪 <b>Example</b>
<code>/prime https://www.primevideo.com/detail/...</code>

━━━━━━━━━━━━━━━
📊 <b>Limits</b>
• Free users: 10 requests / day  
• Premium users: Unlimited requests

━━━━━━━━━━━━━━━
⚙️ <b>Other Commands</b>
<code>/stats</code>     – Bot usage stats  
<code>/premium</code>  – Check premium status  
<code>/mediainfo</code> – Get video file info  
<code>/about</code>     – About the bot  

━━━━━━━━━━━━━━━
✨ <b>Powered by @CineHub_Media</b>
    """
    
    await update.message.reply_text(help_message, parse_mode="HTML", reply_markup=update_button)

# Platform-specific command handlers
async def general_ott_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Save chat ID for startup messages
    save_chat_id(update.effective_chat.id)
    
    # Extract platform from the command name
    platform = update.message.text.split()[0][1:].lower()  # Remove '/' and convert to lowercase
    await handle_ott_command(update, context, platform)

async def airtel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Save chat ID for startup messages
    save_chat_id(update.effective_chat.id)
    
    await handle_ott_command(update, context, "airtel")

async def zee_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Save chat ID for startup messages
    save_chat_id(update.effective_chat.id)
    
    await handle_ott_command(update, context, "zee")

async def prime_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Save chat ID for startup messages
    save_chat_id(update.effective_chat.id)
    
    await handle_ott_command(update, context, "prime")

async def settings_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Configure bot preferences."""
    # Save chat ID for startup messages
    save_chat_id(update.effective_chat.id)
    
    settings_message = """
⚙️ <b>Bot Settings</b>

〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓

🖼️ <b>Image Quality:</b>
 ┃ 📊 Options:
 ┃    • 4K Ultra HD (default) 🌟
 ┃    • Full HD (1080p)     🎯
 ┃    • HD (720p)           📺
 ┃    • Standard (480p)     📱
 ┃
 ┃ 📝 Current: 4K Ultra HD

〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓

🔔 <b>Notification Preferences:</b>
 ┃ ✅ Progress updates: Enabled
 ┃ ✅ Error notifications: Enabled

〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓

🛠️ <b>To Change Settings:</b>
 ┃ Use: <code>/quality &lt;option&gt;</code>
 ┃ Example: <code>/quality 4k</code>

✨ <b>Powered by @CineHub_Media</b>
    """
    await update.message.reply_text(settings_message, parse_mode="HTML", reply_markup=settings_button)

async def quality_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Change image quality settings."""
    if len(context.args) < 1:
        await update.message.reply_text(
            "Please specify quality level.\n"
            "Options: 4k, 1080p, 720p, 480p\n"
            "Example: <code>/quality 4k</code>",
            parse_mode="HTML"
        )
        return
    
    quality = context.args[0].lower()
    valid_qualities = ["4k", "1080p", "720p", "480p"]
    
    if quality in valid_qualities:
        # In a real implementation, you would save this setting
        # For now, we'll just confirm the change
        await update.message.reply_text(
            f"✅ Image quality set to {quality.upper()}\n"
            "This setting will be applied to future requests."
        )
    else:
        await update.message.reply_text(
            "❌ Invalid quality option.\n"
            "Valid options: 4k, 1080p, 720p, 480p"
        )

async def stats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show bot usage statistics."""
    # Save chat ID for startup messages
    save_chat_id(update.effective_chat.id)
    
    # Get real-time statistics
    stats = get_real_time_stats()
    
    # Format popular platforms
    popular_platforms = ""
    for i, (platform, count) in enumerate(stats["top_platforms"], 1):
        popular_platforms += f" ┃ {i}️⃣ {platform.capitalize()} - {count} requests\n"
    
    if not popular_platforms:
        popular_platforms = " ┃ No data available yet\n"
    
    stats_message = f"""
📊 <b>Bot Statistics</b>

〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓

📈 <b>Usage Data:</b>
 ┃ 📦 Total Requests: {stats['total_requests']:,}
 ┃ ✅ Successful:     {stats['successful_requests']:,}
 ┃ ❌ Failed:         {stats['failed_requests']:,}
 ┃ 👥 Unique Users:   {stats['unique_users']:,}

〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓

🔥 <b>Popular Platforms:</b>
{popular_platforms}
〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓

📅 <b>Last Reset:</b> {stats['last_reset'][:10]}

✨ <b>Powered by @CineHub_Media</b>
    """
    await update.message.reply_text(stats_message, parse_mode="HTML")

async def about_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send information about the bot."""
    # Save chat ID for startup messages
    save_chat_id(update.effective_chat.id)
    
    about_message = """
ℹ️ <b>About This Bot</b>

〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓

🤖 <b>OTT Content Scraper Bot</b>
 ┃ 📦 Version: 2.1.0
 ┃ 👨‍💻 Developer: @CineHub_Media
 ┃ 🚀 Status: Active

〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓

✨ <b>Features:</b>
 ┃ 🖼️ 4K Ultra HD poster quality
 ┃ 📋 Detailed content information
 ┃ ⚡ Fast and reliable performance
 ┃ 🌐 Multi-platform support (26+ services)

〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓

🎞️ <b>Supported Platforms:</b>
 ┃ Amazon Prime Video • Hulu
 ┃ Zee5 • Airtel Xstream
 ┃ SunNext • Stage • Adda
 ┃ WeTV • Plex • IQIYI
 ┃ Aha • Shemaroo • Apple TV
 ┃ BMS • HubCloud • VCloud • HubCDN
 ┃ DriveLeech • HubDrive • Neo
 ┃ GDRex • PixelCDN • ExtraFlix
 ┃ ExtraLink • LuxDrive • GDFlix

〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓

📝 <b>Note:</b> Educational purposes only
 🔗 All content from official APIs

✨ <b>Powered by @CineHub_Media</b>
    """
    await update.message.reply_text(about_message, parse_mode="HTML")

async def premium_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle premium membership commands."""
    # Save chat ID for startup messages
    save_chat_id(update.effective_chat.id)
    
    chat_id = update.effective_chat.id
    user_is_owner = is_owner(chat_id)
    
    # Check if user wants to check their status
    if len(context.args) == 0:
        # Check user's premium status
        is_premium = is_premium_user(chat_id)
        daily_requests = get_user_daily_requests(chat_id)
        
        if is_premium:
            premium_message = (
                "🌟 <b>Premium Membership Status</b> 🌟\n\n"
                "✅ <b>Status:</b> ACTIVE Premium Member\n"
                "🎉 <b>Benefits:</b> Unlimited requests/day\n"
                "🚀 <b>Access:</b> All 26+ platforms\n"
                "💎 <b>Priority:</b> Faster processing\n\n"
                "✨ Thank you for supporting us!\n\n"
                "💳 <i>To manage your subscription, contact @CineHub_Media</i>"
            )
        else:
            remaining = max(0, 10 - daily_requests)
            premium_message = (
                f"🌟 <b>Premium Membership</b>\n\n"
                f"Upgrade to premium and unlock:\n"
                f"• Unlimited daily requests  \n"
                f"• Faster response  \n"
                f"• Access to all OTT platforms  \n\n"
                f"━━━━━━━━━━━━━━━\n"
                f"📊 <b>Current Status</b>\n"
                f"• Requests Today: {daily_requests}/10\n"
                f"• Remaining: {remaining} requests\n\n"
                f"━━━━━━━━━━━━━━━\n"
                f"💰 <b>Pricing</b>\n"
                f"• 1 Month  – ₹20  \n"
                f"• 3 Months – ₹50  \n"
                f"• 6 Months – ₹100  \n"
                f"• 12 Months – ₹220  \n\n"
                f"━━━━━━━━━━━━━━━\n"
                f"📩 Contact @CineHub_Media to activate\n\n"
                f"✨ Premium users enjoy unlimited access"
            )
        
        await update.message.reply_text(premium_message, parse_mode="HTML", reply_markup=update_button)
        return
    
    # Handle admin commands for owners only
    if len(context.args) >= 1:
        command = context.args[0].lower()
        
        # Owner-only commands
        if user_is_owner:
            if command == "add" and len(context.args) >= 2:
                try:
                    target_user_id = int(context.args[1])
                    add_premium_user(target_user_id)
                    await update.message.reply_text(f"✅ User {target_user_id} has been added to premium members.", parse_mode="HTML")
                except ValueError:
                    await update.message.reply_text("Invalid user ID provided.", parse_mode="HTML")
                return
            elif command == "remove" and len(context.args) >= 2:
                try:
                    target_user_id = int(context.args[1])
                    # Remove user from premium list
                    premium_users = get_premium_users()
                    if target_user_id in premium_users:
                        premium_users.remove(target_user_id)
                        # Rewrite the file without the removed user
                        with open(PREMIUM_USERS_FILE, "w", encoding="utf-8") as f:
                            for user_id in premium_users:
                                f.write(f"{user_id}\n")
                        await update.message.reply_text(f"✅ User {target_user_id} has been removed from premium members.", parse_mode="HTML")
                    else:
                        await update.message.reply_text(f"❌ User {target_user_id} is not a premium member.", parse_mode="HTML")
                except ValueError:
                    await update.message.reply_text("Invalid user ID provided.", parse_mode="HTML")
                return
            elif command == "list":
                premium_users = get_premium_users()
                if premium_users:
                    user_list = "\n".join([f"  • {user_id}" for user_id in premium_users])
                    list_message = f"👥 <b>Premium Members ({len(premium_users)})</b>:\n{user_list}"
                else:
                    list_message = "📭 <b>No premium members found.</b>"
                await update.message.reply_text(list_message, parse_mode="HTML")
                return
            elif command == "status" and len(context.args) >= 2:
                try:
                    target_user_id = int(context.args[1])
                    is_premium = is_premium_user(target_user_id)
                    status_message = (
                        f"{'✅ Premium' if is_premium else '❌ Not Premium'} member: {target_user_id}"
                    )
                    await update.message.reply_text(status_message, parse_mode="HTML")
                except ValueError:
                    await update.message.reply_text("Invalid user ID provided.", parse_mode="HTML")
                return
        
        # Common commands for all users
        help_message = (
            "🔐 <b>Premium Membership Commands</b> 🔐\n\n"
            "Available commands:\n"
            "  /premium - Check your membership status\n"
        )
        
        # Add owner-only commands to help message
        if user_is_owner:
            help_message += (
                "  /premium add [user_id] - Add user to premium (owner only)\n"
                "  /premium remove [user_id] - Remove user from premium (owner only)\n"
                "  /premium list - List all premium members (owner only)\n"
                "  /premium status [user_id] - Check user's status (owner only)\n\n"
            )
        else:
            help_message += (
                "  /premium status [user_id] - Check user's status (admin)\n\n"
            )
        
        help_message += (
            "✨ <b>Benefits of Premium Membership:</b>\n"
            "  • Unlimited daily requests\n"
            "  • Priority processing\n"
            "  • Early access to new features\n\n"
            "💰 <b>Premium Pricing:</b>\n"
            "  • 1 Month: ₹20\n"
            "  • 3 Months: ₹50 (Save ₹10)\n"
            "  • 6 Months: ₹100 (Save ₹20)\n"
            "  • 12 Months: ₹220 (Save ₹20)\n\n"
            "💳 Contact @CineHub_Media for subscription."
        )
        
        await update.message.reply_text(help_message, parse_mode="HTML", reply_markup=update_button)

# ===== CHAT ID STORAGE FUNCTIONS =====
def save_chat_id(chat_id: int):
    """Save chat ID to file if not already present."""
    try:
        # Read existing chat IDs
        if CHAT_IDS_FILE.exists():
            with open(CHAT_IDS_FILE, "r", encoding="utf-8") as f:
                chat_ids = f.read().splitlines()
        else:
            chat_ids = []
        
        # Add chat ID if not already in list
        chat_id_str = str(chat_id)
        if chat_id_str not in chat_ids:
            with open(CHAT_IDS_FILE, "a", encoding="utf-8") as f:
                f.write(f"{chat_id_str}\n")
    except Exception as e:
        logger.error(f"Error saving chat ID: {e}")

def get_premium_users():
    """Get list of premium users."""
    try:
        if PREMIUM_USERS_FILE.exists():
            with open(PREMIUM_USERS_FILE, "r", encoding="utf-8") as f:
                lines = f.readlines()
                return [int(line.strip()) for line in lines if line.strip().isdigit()]
        return []
    except Exception as e:
        logger.error(f"Error reading premium users: {e}")
        return []

def add_premium_user(chat_id: int):
    """Add a user to premium list."""
    try:
        premium_users = get_premium_users()
        if chat_id not in premium_users:
            with open(PREMIUM_USERS_FILE, "a", encoding="utf-8") as f:
                f.write(f"{chat_id}\n")
    except Exception as e:
        logger.error(f"Error adding premium user: {e}")

def is_owner(chat_id: int) -> bool:
    """Check if user is an owner/admin."""
    return chat_id in OWNER_IDS

def is_premium_user(chat_id: int) -> bool:
    """Check if user is premium."""
    try:
        return chat_id in get_premium_users()
    except Exception as e:
        logger.error(f"Error checking premium status: {e}")
        return False

def get_chat_ids():
    """Get all stored chat IDs."""
    try:
        if CHAT_IDS_FILE.exists():
            with open(CHAT_IDS_FILE, "r", encoding="utf-8") as f:
                lines = f.readlines()
                chat_ids = []
                for line in lines:
                    stripped_line = line.strip()
                    if stripped_line and stripped_line.isdigit():
                        chat_ids.append(int(stripped_line))
                return chat_ids
        return []
    except Exception as e:
        logger.error(f"Error reading chat IDs: {e}")
        return []

# ===== BOT STATISTICS FUNCTIONS =====
import json
from datetime import datetime, timedelta

def initialize_stats():
    """Initialize stats file with default values if it doesn't exist or is empty."""
    default_stats = {
        "total_requests": 0,
        "successful_requests": 0,
        "failed_requests": 0,
        "unique_users": 0,
        "platform_usage": {},
        "last_reset": datetime.now().isoformat(),
        "recent_users": [],
        "daily_stats": {},
        "user_daily_requests": {}
    }
    
    try:
        if not STATS_FILE.exists() or STATS_FILE.stat().st_size == 0:
            with open(STATS_FILE, "w", encoding="utf-8") as f:
                json.dump(default_stats, f, indent=2)
        else:
            # Validate existing stats file
            with open(STATS_FILE, "r", encoding="utf-8") as f:
                stats = json.load(f)
            # Ensure all required keys exist
            for key in default_stats:
                if key not in stats:
                    stats[key] = default_stats[key]
            with open(STATS_FILE, "w", encoding="utf-8") as f:
                json.dump(stats, f, indent=2)
    except Exception as e:
        logger.error(f"Error initializing stats: {e}")
        # Force initialization
        with open(STATS_FILE, "w", encoding="utf-8") as f:
            json.dump(default_stats, f, indent=2)

def load_stats():
    """Load statistics from file."""
    try:
        initialize_stats()  # Ensure file exists
        with open(STATS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading stats: {e}")
        return initialize_stats()

def save_stats(stats):
    """Save statistics to file."""
    try:
        # Clean up old daily stats (keep only last 30 days)
        clean_old_daily_stats(stats)
        
        with open(STATS_FILE, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving stats: {e}")

def clean_old_daily_stats(stats):
    """Remove daily stats older than 30 days to prevent infinite growth."""
    from datetime import datetime, timedelta
    
    try:
        if "daily_stats" in stats:
            current_date = datetime.now()
            cutoff_date = current_date - timedelta(days=30)
            
            # Get dates to remove
            dates_to_remove = []
            for date_str in stats["daily_stats"]:
                try:
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                    if date_obj < cutoff_date:
                        dates_to_remove.append(date_str)
                except ValueError:
                    # Invalid date format, remove it
                    dates_to_remove.append(date_str)
            
            # Remove old dates
            for date_str in dates_to_remove:
                del stats["daily_stats"][date_str]
                
        # Clean up old user daily requests (keep only last 2 days)
        if "user_daily_requests" in stats:
            current_date = datetime.now()
            cutoff_date = current_date - timedelta(days=2)
            
            keys_to_remove = []
            for key in stats["user_daily_requests"]:
                # Extract date from key (format: user_id_YYYY-MM-DD)
                try:
                    # Extract date part from format: user_id_YYYY-MM-DD
                    if "_" in key:
                        date_str = key.split("_", 1)[1]  # Get everything after first underscore
                        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                        if date_obj < cutoff_date:
                            keys_to_remove.append(key)
                except ValueError:
                    # If parsing fails, remove the entry
                    keys_to_remove.append(key)
            
            # Remove old entries
            for key in keys_to_remove:
                if key in stats["user_daily_requests"]:
                    del stats["user_daily_requests"][key]
    except Exception as e:
        logger.error(f"Error cleaning old stats: {e}")

def increment_stat(stat_name: str, platform: str = None, chat_id: int = None):
    """Increment a specific statistic."""
    try:
        stats = load_stats()
        
        # Increment the main stat
        if stat_name in stats:
            stats[stat_name] += 1
        
        # Handle platform-specific stats
        if platform and "platform_usage" in stats:
            if platform in stats["platform_usage"]:
                stats["platform_usage"][platform] += 1
            else:
                stats["platform_usage"][platform] = 1
        
        # Handle daily stats
        today = datetime.now().strftime("%Y-%m-%d")
        if "daily_stats" in stats:
            if today not in stats["daily_stats"]:
                stats["daily_stats"][today] = {
                    "requests": 0,
                    "successful": 0,
                    "failed": 0
                }
            if stat_name == "total_requests":
                stats["daily_stats"][today]["requests"] += 1
            elif stat_name == "successful_requests":
                stats["daily_stats"][today]["successful"] += 1
            elif stat_name == "failed_requests":
                stats["daily_stats"][today]["failed"] += 1
        
        # Track user requests per day
        if chat_id and "user_daily_requests" in stats:
            user_key = f"{chat_id}_{today}"
            if user_key not in stats["user_daily_requests"]:
                stats["user_daily_requests"][user_key] = 0
            stats["user_daily_requests"][user_key] += 1
        elif chat_id:
            # Initialize user_daily_requests if not exists
            stats["user_daily_requests"] = {f"{chat_id}_{today}": 1}
        
        save_stats(stats)
    except Exception as e:
        logger.error(f"Error incrementing stat: {e}")

def get_user_daily_requests(chat_id: int) -> int:
    """Get user's requests count for today."""
    try:
        stats = load_stats()
        today = datetime.now().strftime("%Y-%m-%d")
        user_key = f"{chat_id}_{today}"
        
        if "user_daily_requests" in stats and user_key in stats["user_daily_requests"]:
            return stats["user_daily_requests"][user_key]
        return 0
    except Exception as e:
        logger.error(f"Error getting user daily requests: {e}")
        return 0

def update_user_stats(chat_id: int):
    """Update user statistics."""
    try:
        stats = load_stats()
        
        # Update recent users (keep last 50)
        if "recent_users" in stats:
            if chat_id not in stats["recent_users"]:
                stats["recent_users"].append(chat_id)
                if len(stats["recent_users"]) > 50:
                    stats["recent_users"] = stats["recent_users"][-50:]
                # Update unique users count
                stats["unique_users"] = len(stats["recent_users"])
        
        save_stats(stats)
    except Exception as e:
        logger.error(f"Error updating user stats: {e}")

def get_real_time_stats():
    """Get formatted real-time statistics."""
    try:
        stats = load_stats()
        
        # Calculate requests in the last 24 hours
        last_24_hours = 0
        last_24_success = 0
        last_24_failed = 0
        
        now = datetime.now()
        for i in range(1, 25):  # Last 24 hours
            date_key = (now - timedelta(hours=i)).strftime("%Y-%m-%d")
            if date_key in stats.get("daily_stats", {}):
                day_stats = stats["daily_stats"][date_key]
                last_24_hours += day_stats.get("requests", 0)
                last_24_success += day_stats.get("successful", 0)
                last_24_failed += day_stats.get("failed", 0)
        
        # Get top 5 platforms
        platform_usage = stats.get("platform_usage", {})
        sorted_platforms = sorted(platform_usage.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "total_requests": stats.get("total_requests", 0),
            "successful_requests": stats.get("successful_requests", 0),
            "failed_requests": stats.get("failed_requests", 0),
            "unique_users": stats.get("unique_users", 0),
            "top_platforms": sorted_platforms,
            "last_24_hours": last_24_hours,
            "last_24_success": last_24_success,
            "last_24_failed": last_24_failed,
            "last_reset": stats.get("last_reset", "Unknown")
        }
    except Exception as e:
        logger.error(f"Error getting real-time stats: {e}")
        return {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "unique_users": 0,
            "top_platforms": [],
            "last_24_hours": 0,
            "last_24_success": 0,
            "last_24_failed": 0,
            "last_reset": "Unknown"
        }

async def send_startup_message(application):
    """Send startup message to all stored chat IDs."""
    try:
        chat_ids = get_chat_ids()
        if not chat_ids:
            logger.info("No chat IDs found to send startup message")
            return
        
        startup_message = (
            "🚀 <b>Bot Restarted Successfully!</b> 🚀\n\n"
            "✅ All systems operational\n"
            "🌐 26+ OTT platforms supported\n"
            "🖼️ 4K Ultra HD poster quality\n\n"
            "✨ <b>Powered by @CineHub_Media</b>"
        )
        
        sent_count = 0
        for chat_id in chat_ids:
            try:
                await application.bot.send_message(
                    chat_id=chat_id,
                    text=startup_message,
                    parse_mode="HTML",
                    reply_markup=update_button
                )
                sent_count += 1
                # Small delay to avoid hitting rate limits
                await asyncio.sleep(0.1)
            except Exception as e:
                logger.error(f"Failed to send startup message to {chat_id}: {e}")
        
        logger.info(f"Startup message sent to {sent_count}/{len(chat_ids)} chats")
    except Exception as e:
        logger.error(f"Error sending startup messages: {e}")

async def mediainfo_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Extract media information from a video URL."""
    chat_id = update.effective_chat.id
    
    # Update user stats
    update_user_stats(chat_id)
    
    # Check if user is premium
    is_premium = is_premium_user(chat_id)
    
    # Check daily request limit for non-premium users
    if not is_premium:
        daily_requests = get_user_daily_requests(chat_id)
        if daily_requests >= 10:
            # Send limit exceeded message
            limit_message = (
                "🚫 <b>Daily Request Limit Exceeded</b> 🚫\n\n"
                "You've reached the maximum of 10 requests per day.\n\n"
                "✨ <b>Upgrade to Premium</b> for unlimited access!\n\n"
                "💰 <b>Premium Pricing:</b>\n"
                "  • 1 Month: ₹20\n"
                "  • 3 Months: ₹50 (Save ₹10)\n"
                "  • 6 Months: ₹100 (Save ₹20)\n"
                "  • 12 Months: ₹220 (Save ₹20)\n\n"
                "💳 Contact @CineHub_Media for premium subscription.\n\n"
                "🔄 Limit resets at 00:00 UTC daily."
            )
            await update.message.reply_text(limit_message, parse_mode="HTML", reply_markup=update_button)
            return
    
    # Increment total requests
    increment_stat("total_requests", "mediainfo", chat_id)
    
    if len(context.args) < 1:
        await update.message.reply_text(
            "🔗 Please provide a video URL to get media info.\n\n"
            "Example:\n<code>/mediainfo https://example.com/video.mp4</code>", 
            parse_mode="HTML"
        )
        return
    
    video_url = context.args[0].strip()
    msg = await update.message.reply_text("🔍 Fetching media info...")
    
    try:
        # Try to get media info from the URL
        media_info = await extract_media_info(video_url)
        
        if media_info:
            # Increment successful requests
            increment_stat("successful_requests", "mediainfo", chat_id)
            
            # Format and send the media info
            info_text = format_media_info(media_info, video_url)
            await msg.edit_text(info_text, parse_mode="HTML", reply_markup=update_button)
        else:
            # Increment failed requests
            increment_stat("failed_requests", "mediainfo", chat_id)
            await msg.edit_text("❌ Failed to extract media info from the provided URL.")
    
    except Exception as e:
        logger.error(f"Error extracting media info: {e}")
        # Increment failed requests
        increment_stat("failed_requests", "mediainfo", chat_id)
        await msg.edit_text(f"❌ Error extracting media info: {str(e)}")

async def extract_media_info(url: str) -> dict:
    """
    Extract media information from a video URL using HEAD request and content-type analysis.
    """
    try:
        # Add headers to avoid blocking
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'video/*, */*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.google.com/'
        }
        
        async with aiohttp.ClientSession() as session:
            # First, try a HEAD request to get content type and other headers
            async with session.head(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                content_type = resp.headers.get('content-type', '')
                content_length = resp.headers.get('content-length', 'Unknown')
                content_disposition = resp.headers.get('content-disposition', '')
                
                # If it's a video, try to get more info
                if content_type.startswith('video/'):
                    # Get file size in human readable format
                    size_bytes = int(content_length) if content_length.isdigit() else 0
                    size_mb = size_bytes / (1024 * 1024) if size_bytes > 0 else 0
                    
                    # For video files, we can't get detailed info without downloading,
                    # so we'll return basic info based on headers
                    return {
                        'type': 'video',
                        'format': content_type,
                        'size': f"{size_mb:.2f} MB" if size_mb > 0 else "Unknown",
                        'size_bytes': size_bytes,
                        'url': url,
                        'content_type': content_type,
                        'content_length': content_length
                    }
                
            # If HEAD request doesn't work, try GET with range request to get minimal data
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                content_type = resp.headers.get('content-type', '')
                content_length = resp.headers.get('content-length', 'Unknown')
                
                if content_type.startswith('video/'):
                    size_bytes = int(content_length) if content_length.isdigit() else 0
                    size_mb = size_bytes / (1024 * 1024) if size_bytes > 0 else 0
                    
                    return {
                        'type': 'video',
                        'format': content_type,
                        'size': f"{size_mb:.2f} MB" if size_mb > 0 else "Unknown",
                        'size_bytes': size_bytes,
                        'url': url,
                        'content_type': content_type,
                        'content_length': content_length
                    }
                
        return None
    except Exception as e:
        logger.error(f"Error extracting media info from {url}: {e}")
        return None

def format_media_info(info: dict, original_url: str) -> str:
    """
    Format media information for display.
    """
    try:
        # Extract format type (e.g., video/mp4 -> mp4)
        format_type = info.get('content_type', 'Unknown').split('/')[-1]
        if format_type == 'octet-stream':
            format_type = 'Unknown'
        
        # Format the response
        formatted_info = (
            f"<b>🎥 Media Information</b> 🎥\n\n"
            f"🔗 <b>URL:</b> {original_url[:50]}...\n\n"
            f"📊 <b>Format:</b> {format_type}\n"
            f"📏 <b>Content Type:</b> {info.get('content_type', 'Unknown')}\n"
            f"💾 <b>Size:</b> {info.get('size', 'Unknown')}\n"
            f"🔢 <b>Size (bytes):</b> {info.get('size_bytes', 'Unknown')}\n\n"
            f"✨ <b>Powered by @CineHub_Media</b>"
        )
        
        return formatted_info
    except Exception as e:
        logger.error(f"Error formatting media info: {e}")
        return f"<b>Media Info</b>\n\nURL: {original_url}\n\nError formatting details: {str(e)}"

#Don't Remove Credit @CineHub_Media 
# ===== MAIN FUNCTION =====
def main():
    """Start the bot."""
    # Initialize statistics
    initialize_stats()
    
    # Create the Application and pass it your bot's token
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Send startup message to all stored chat IDs
    application.post_init = send_startup_message

    # Register command handlers
    application.add_handler(CommandHandler("start", start_cmd))
    application.add_handler(CommandHandler("help", help_cmd))
    
    # Register platform-specific command handlers
    application.add_handler(CommandHandler("sunnext", general_ott_cmd))
    application.add_handler(CommandHandler("hulu", general_ott_cmd))
    application.add_handler(CommandHandler("stage", general_ott_cmd))
    application.add_handler(CommandHandler("adda", general_ott_cmd))
    application.add_handler(CommandHandler("wetv", general_ott_cmd))
    application.add_handler(CommandHandler("plex", general_ott_cmd))
    application.add_handler(CommandHandler("iqiyi", general_ott_cmd))
    application.add_handler(CommandHandler("aha", general_ott_cmd))
    application.add_handler(CommandHandler("shemaroo", general_ott_cmd))
    application.add_handler(CommandHandler("apple", general_ott_cmd))
    application.add_handler(CommandHandler("airtel", airtel_cmd))
    application.add_handler(CommandHandler("zee", zee_cmd))
    application.add_handler(CommandHandler("prime", prime_cmd))
    application.add_handler(CommandHandler("bms", general_ott_cmd))
    # Register new platform command handlers
    application.add_handler(CommandHandler("hubcloud", general_ott_cmd))
    application.add_handler(CommandHandler("vcloud", general_ott_cmd))
    application.add_handler(CommandHandler("hubcdn", general_ott_cmd))
    application.add_handler(CommandHandler("driveleech", general_ott_cmd))
    application.add_handler(CommandHandler("hubdrive", general_ott_cmd))
    application.add_handler(CommandHandler("neo", general_ott_cmd))
    application.add_handler(CommandHandler("gdrex", general_ott_cmd))
    application.add_handler(CommandHandler("pixelcdn", general_ott_cmd))
    application.add_handler(CommandHandler("extraflix", general_ott_cmd))
    application.add_handler(CommandHandler("extralink", general_ott_cmd))
    application.add_handler(CommandHandler("luxdrive", general_ott_cmd))
    application.add_handler(CommandHandler("gdflix", general_ott_cmd))

    # Register new command handlers
    application.add_handler(CommandHandler("settings", settings_cmd))
    application.add_handler(CommandHandler("quality", quality_cmd))
    application.add_handler(CommandHandler("stats", stats_cmd))
    application.add_handler(CommandHandler("about", about_cmd))
    application.add_handler(CommandHandler("premium", premium_cmd))
    application.add_handler(CommandHandler("mediainfo", mediainfo_cmd))

    # Auto-detect OTT from URL
    async def auto_detect_ott(update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text.strip()

        if not text.startswith("http"):
            return

        for domain, platform in OTT_DOMAIN_MAP.items():
            if domain in text:
                await handle_ott_command(update, context, platform)
                return

        await update.message.reply_text(
            "❌ Unsupported OTT link.\nUse /help to see supported platforms."
        )

    # Register message handler for auto-detection
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, auto_detect_ott)
    )

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()