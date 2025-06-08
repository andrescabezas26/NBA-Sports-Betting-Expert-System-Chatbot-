# run_local.py - For local development with polling

import os
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler
from telegram_bot import (
    start, choose_teams, handle_team_input, handle_team2_input, 
    handle_venue_choice, handle_betting_team_choice, handle_continue_choice, 
    cancel, CHOOSING_TEAMS, ENTER_TEAM_NAMES, ENTER_TEAM2, 
    CHOOSE_VENUE, CHOOSE_BETTING_TEAM, CONTINUE_OR_END
)

if __name__ == '__main__':
    load_dotenv()
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING_TEAMS: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_teams)],
            ENTER_TEAM_NAMES: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_team_input)],
            ENTER_TEAM2: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_team2_input)],
            CHOOSE_VENUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_venue_choice)],
            CHOOSE_BETTING_TEAM: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_betting_team_choice)],
            CONTINUE_OR_END: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_continue_choice)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    app.add_handler(conv_handler)
    print("✅ Bot running locally with polling...")

    app.run_polling()
