import asyncio
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ConversationHandler, filters
from utils.config import Config
from utils.logger import logger
from services.database import db_service

# Import handlers
from handlers.start import start_command, menu_callback
from handlers.chat import handle_user_chat, feedback_callback
from handlers.faq import faq_command, faq_routing_callback
from handlers.support import start_support_ticket, ticket_name, ticket_email, ticket_desc, cancel_ticket, NAME, EMAIL, DESC
from handlers.settings import settings_command, settings_toggle_callback
from handlers.about import about_command
from handlers.admin import admin_command, admin_broadcast

async def main():
    # 1. Validate variables configuration environment definitions
    Config.validate()
    
    # 2. Instantiate and generate system DB records tables maps
    await db_service.init_db()

    # 3. Initialize deployment application object structure
    application = Application.builder().token(Config.BOT_TOKEN).build()

    # 4. Integrate core configuration state routing conversational models
    ticket_conv = ConversationHandler(
        entry_points=[
            CommandHandler("support", start_support_ticket),
            CallbackQueryHandler(start_support_ticket, pattern="^contact_support$")
        ],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ticket_name)],
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, ticket_email)],
            DESC: [MessageHandler(filters.TEXT & ~filters.COMMAND, ticket_desc)],
        },
        fallbacks=[CommandHandler("cancel", cancel_ticket)],
        allow_reentry=True
    )

    # 5. Connect and map all input Command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("faq", faq_command))
    application.add_handler(CommandHandler("settings", settings_command))
    application.add_handler(CommandHandler("about", about_command))
    application.add_handler(CommandHandler("admin", admin_command))
    application.add_handler(CommandHandler("broadcast", admin_broadcast))
    
    # Add Conversational Escalation Block Engine
    application.add_handler(ticket_conv)

    # 6. Map and bind query feedback networks interactions callbacks
    application.add_handler(CallbackQueryHandler(menu_callback, pattern="^main_menu$"))
    application.add_handler(CallbackQueryHandler(faq_command, pattern="^view_faqs$"))
    application.add_handler(CallbackQueryHandler(faq_routing_callback, pattern="^faq_"))
    application.add_handler(CallbackQueryHandler(settings_command, pattern="^open_settings$"))
    application.add_handler(CallbackQueryHandler(settings_toggle_callback, pattern="^toggle_"))
    application.add_handler(CallbackQueryHandler(about_command, pattern="^view_about$"))
    application.add_handler(CallbackQueryHandler(feedback_callback, pattern="^rate_"))
    
    # Fallback to AI execution processor when receiving default textual entries
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_chat))

    # 7. Start application engine execution polling loops
    logger.info("Initializing runtime execution pooling. Engine Active.")
    await application.initialize()
    await application.start()
    await application.updater.start_polling(drop_pending_updates=True)
    
    # Block running context safely to keep asynchronous event execution cycles spinning
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("System loop execution intercepted. Terminating engine runtime environment state gracefully.")
