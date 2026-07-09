from telegram import Update
from telegram.ext import ContextTypes
from services.database import db_service
from keyboards.inline import get_settings_menu

async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    curr = await db_service.get_user_settings(user_id)
    
    text = "⚙ *User Configuration Engine*\nAdjust language arrays, length outputs, and telemetry state tracking memory rules."
    if update.message:
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=get_settings_menu(curr))
    elif update.callback_query:
        await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_settings_menu(curr))

async def settings_toggle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    curr = await db_service.get_user_settings(user_id)
    action = query.data

    if action == "toggle_lang":
        new_lang = "es" if curr["language"] == "en" else "en"
        await db_service.update_user_setting(user_id, "language", new_lang)
    elif action == "toggle_style":
        styles = ["Concise", "Balanced", "Detailed"]
        new_style = styles[(styles.index(curr["style"]) + 1) % len(styles)]
        await db_service.update_user_setting(user_id, "style", new_style)
    elif action == "toggle_history":
        new_hist = 0 if curr["history_enabled"] else 1
        await db_service.update_user_setting(user_id, "history_enabled", new_hist)

    updated_curr = await db_service.get_user_settings(user_id)
    await query.answer("Configuration updated.")
    await query.edit_message_markup(reply_markup=get_settings_menu(updated_curr))
