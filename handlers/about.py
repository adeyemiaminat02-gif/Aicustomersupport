from telegram import Update
from telegram.ext import ContextTypes

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    about_text = (
        f"ℹ️ *About Our Assistant Engine*\n\n"
        f"*Bot Name:* @AICustomerSupportsBot\n"
        f"*System Version:* 1.2.0-Stable\n"
        f"*Runtime Engine:* Python 3.12 Architecture\n\n"
        f"Powered by custom Isolated Language Processing pipelines running standard neural layers "
        f"integrated directly with real-time application database modules."
    )
    if update.message:
        await update.message.reply_text(about_text, parse_mode="Markdown")
    elif update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(about_text, parse_mode="Markdown")
