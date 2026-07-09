from telegram import Update
from telegram.ext import ContextTypes
from services.ai_service import ai_service
from keyboards.inline import get_post_chat_menu

async def handle_user_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_msg = update.message.text

    # Basic anti-spam configuration
    if len(user_msg) > 600:
        await update.message.reply_text("⚠️ Message string length exceeds structural safety limits. Please simplify your query.")
        return

    # User typing indicator action
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    ai_response = await ai_service.get_reply(user_id, user_msg)
    await update.message.reply_text(ai_response, reply_markup=get_post_chat_menu())

async def feedback_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    rating = "Helpful" if query.data == "rate_good" else "Not Helpful"
    
    await db_service.save_feedback(user_id, rating)
    await query.answer("Thank you for your rating!", show_alert=False)
    await query.edit_message_text(
        f"✨ *Thank you for your response!*\nYour rating has been recorded to improve system parameters.",
        parse_mode="Markdown",
        reply_markup=get_post_chat_menu()
    )
