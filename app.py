import os
import sys
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ConversationHandler, filters
from utils.config import Config
from utils.logger import logger
from services.database import db_service

# Import functional feature handlers
from handlers.start import start_command, menu_callback
from handlers.chat import handle_user_chat, feedback_callback
from handlers.faq import faq_command, faq_routing_callback
from handlers.support import start_support_ticket, ticket_name, ticket_email, ticket_desc, cancel_ticket, NAME, EMAIL, DESC
from handlers.settings import settings_command, settings_toggle_callback
from handlers.about import about_command
from handlers.admin import admin_command, admin_broadcast

def initialize_environment():
    """Ensure runtime directories and configurations are perfectly set before boot."""
    try:
        # Force create data directory to prevent folder-not-found crashes on Render
        os.makedirs("data", exist_ok=True)
        
        # Validate critical environment variables
        Config.validate()
        logger.info("Environment configurations validated successfully.")
    except Exception as e:
        logger.critical(f"Environment initialization failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # 1. Prepare workspace folders and run structural checks
    initialize_environment()
    
    try:
        # 2. Instantiate the foundational PTB Application structure
        application = Application.builder().token(Config.BOT_TOKEN).build()

        # 3. Configure the stateful Human Support Escalation Conversation Engine
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

        # 4. Attach Command Handlers
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("faq", faq_command))
        application.add_handler(CommandHandler("settings", settings_command))
        application.add_handler(CommandHandler("about", about_command))
        application.add_handler(CommandHandler("admin", admin_command))
        application.add_handler(CommandHandler("broadcast", admin_broadcast))
        
        # Attach the multi-step support ticket ticket processor
        application.add_handler(ticket_conv)

        # 5. Attach Inline Interface Interactive Callbacks
        application.add_handler(CallbackQueryHandler(menu_callback, pattern="^main_menu$"))
        application.add_handler(CallbackQueryHandler(faq_command, pattern="^view_faqs$"))
        application.add_handler(CallbackQueryHandler(faq_routing_callback, pattern="^faq_"))
        application.add_handler(CallbackQueryHandler(settings_command, pattern="^open_settings$"))
        application.add_handler(CallbackQueryHandler(settings_toggle_callback, pattern="^toggle_"))
        application.add_handler(CallbackQueryHandler(about_command, pattern="^view_about$"))
        application.add_handler(CallbackQueryHandler(feedback_callback, pattern="^rate_"))
        
        # 6. Default Fallback Handler: Send any unstructured text directly to the AI Engine
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_chat))

        # 7. Start the Natively Managed Background Worker Loop
        logger.info("Initializing natively managed Background Worker loop. Engine Active.")
        
        # run_polling automatically handles application initialize, start, polling, and clean stop loops.
        # drop_pending_updates ignores old backlogged messages sent while the bot was offline.
        application.run_polling(drop_pending_updates=True)

    except (KeyboardInterrupt, SystemExit):
        logger.info("System loop execution intercepted. Terminating engine runtime state gracefully.")
    except Exception as e:
        logger.critical(f"Fatal crash during startup sequence: {e}", exc_info=True)
