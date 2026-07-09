from telegram import Update
from telegram.ext import ContextTypes
from keyboards.inline import get_main_menu
from services.database import db_service

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await db_service.get_user_settings(user.id) # Warm up user row
    
    welcome_text = (
        f"🤖 *Welcome to AI Customer Supports Bot!*\n\n"
        f"Hello {user.first_name}, I'm your virtual customer support assistant. "
        f"I can answer natural questions, manage FAQs, handle escalation tickets, "
        f"and bridge your questions seamlessly with human supervisors."
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown", reply_markup=get_main_menu())

async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    welcome_text = (
        f"🤖 *AI Customer Support Hub*\n"
        f"Please select an option below to interact with our systems."
    )
    await query.edit_message_text(welcome_text, parse_mode="Markdown", reply_markup=get_main_menu())
