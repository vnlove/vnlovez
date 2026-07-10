import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

TOKEN = os.environ.get("ap_key_telegram_dvtbot", "")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Xin chào! Tôi là DVT BOT 🤖\nGõ /help để xem danh sách lệnh.")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "/start - Khởi động bot\n"
        "/help - Danh sách lệnh\n"
        "/info - Thông tin bot\n"
    )
    await update.message.reply_text(text)


async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    me = await bot.get_me()
    text = (
        f"Bot: {me.first_name}\n"
        f"Username: @{me.username}\n"
        f"ID: {me.id}\n"
    )
    await update.message.reply_text(text)


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Bạn nói: {update.message.text}")


def main():
    if not TOKEN:
        print("ERROR: Không tìm thấy API key. Đặt biến môi trường ap_key_telegram_dvtbot")
        return

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("info", info))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    print("DVT BOT đang chạy...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
