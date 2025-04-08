import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes
)
from yt_dlp import YoutubeDL

# --- Config ---
TOKEN = "7342053757:AAE3ohfeFqQN9zSWxYVoUJaHeOdvpFiX1TQ"  # From @BotFather
LYRICS_API_KEY = "s0Gxt_vwG7muW0CiPgrmk_7LbHxC8CLoLNPhnzwD0SqMC3iKC2MzC_wJhQ9uNofIZFBTYhrRWZuVeA94M2Qc6g"  # Optional: Get from genius.com/api-clients

# --- Initialize ---
async def cleanup(application: Application):
    """Ensure webhook is deleted before starting"""
    await application.bot.delete_webhook(drop_pending_updates=True)

# --- Commands ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎵 Music Bot\n\n"
        "Commands:\n"
        "/play [song] - Stream music\n"
        "/lyrics [song] - Get lyrics"
    )

async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = " ".join(context.args)
        if not query:
            await update.message.reply_text("❌ Please specify a song (e.g. /play Bohemian Rhapsody)")
            return

        # Download audio info (no full download)
        ydl_opts = {
            'format': 'bestaudio/best',
            'extract_flat': True,
            'quiet': True
        }
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch1:{query}", download=False)
            url = info['entries'][0]['url']
            title = info['entries'][0]['title']

        # Send audio stream directly from URL
        await update.message.reply_audio(
            audio=url,
            title=title,
            performer="Music Bot",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("📝 Lyrics", callback_data=f"lyrics_{title}")
            ]])
        )

    except Exception as e:
        await update.message.reply_text(f"⚠️ Error: {str(e)}")

async def lyrics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fetch lyrics via Genius API or Google fallback"""
    query = " ".join(context.args) or update.callback_query.data.replace("lyrics_", "")
    
    try:
        # Try Genius API first
        if LYRICS_API_KEY:
            response = requests.get(
                f"https://api.genius.com/search?q={query}",
                headers={"Authorization": f"Bearer {LYRICS_API_KEY}"}
            )
            lyrics_url = response.json()['response']['hits'][0]['result']['url']
            await update.message.reply_text(f"🎤 {query}\n{lyrics_url}")
        else:
            # Fallback to Google search
            await update.message.reply_text(
                f"🔍 Lyrics for {query}:\n"
                f"https://www.google.com/search?q=lyrics+{query.replace(' ', '+')}"
            )
    except Exception:
        await update.message.reply_text("❌ Couldn't find lyrics")

# --- Main ---
def main():
    # Create Application with cleanup handler
    application = Application.builder() \
        .token(TOKEN) \
        .post_init(cleanup) \  # Ensures webhook is deleted
        .build()

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("play", play))
    application.add_handler(CommandHandler("lyrics", lyrics))
    application.add_handler(CallbackQueryHandler(lyrics, pattern="^lyrics_"))

    # Start polling
    print("Bot running...")
    application.run_polling(drop_pending_updates=True)  # Avoid processing old updates

if __name__ == "__main__":
    main()
