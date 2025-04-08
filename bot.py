import os
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters,
    ContextTypes  # Critical import
)
from yt_dlp import YoutubeDL

TOKEN = "7342053757:AAE3ohfeFqQN9zSWxYVoUJaHeOdvpFiX1TQ"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎵 Send /play [song name] to stream music!")

async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        song = " ".join(context.args)
        if not song:
            await update.message.reply_text("❌ Please type: /play [song name]")
            return

        ydl_opts = {'format': 'bestaudio/best', 'quiet': True}
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch1:{song}", download=False)
            url = info['entries'][0]['url']

        await update.message.reply_audio(audio=url, title=song)
        await update.message.reply_text(f"📝 Lyrics: https://www.google.com/search?q=lyrics+{song.replace(' ', '+')}")

    except Exception as e:
        await update.message.reply_text(f"⚠️ Error: {str(e)}")

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("play", play))

if __name__ == "__main__":
    print("Bot running...")
    app.run_polling()