import os
import logging
import asyncio
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters,
    ContextTypes, ConversationHandler
)
from nba_chatbot import NBAChatbot

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation states
CHOOSING_TEAMS, ENTER_TEAM_NAMES, ENTER_TEAM2, CHOOSE_VENUE, CHOOSE_BETTING_TEAM, CONTINUE_OR_END = range(6)

chatbot = NBAChatbot()

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏀 Welcome to the NBA Sports Betting Bot!\n"
        "What would you like to do?\n"
        "1️⃣ View upcoming games\n"
        "2️⃣ Enter teams manually",
        reply_markup=ReplyKeyboardMarkup([['1', '2']], one_time_keyboard=True, resize_keyboard=True)
    )
    return CHOOSING_TEAMS

# Choice between games or manual entry
async def choose_teams(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text == '1':
        games = chatbot.display_upcoming_games()
        context.user_data['games'] = games
        if not games:
            await update.message.reply_text("No games found. Enter teams manually.")
            return await ask_manual(update, context)
        else:
            message = "These are the upcoming games:\n"
            for idx, game in enumerate(games, 1):
                message += f"{idx}. {game.away_team} @ {game.home_team}\n"
            message += "\nReply with the number of the game you want to analyze."
            await update.message.reply_text(message)
            return ENTER_TEAM_NAMES
    elif text == '2':
        return await ask_manual(update, context)
    else:
        await update.message.reply_text("❌ Invalid option. Type 1 or 2.")
        return CHOOSING_TEAMS

# Manual team entry
async def ask_manual(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📝 Enter two NBA teams to analyze:\n\n💡 Tip: You can use names like 'Lakers', 'Warriors', 'Celtics', etc.\n\nType the name of the first team:")
    context.user_data['manual_input'] = True
    context.user_data['step'] = 'team1'
    return ENTER_TEAM_NAMES

# Receive team names
async def handle_team_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    manual = context.user_data.get('manual_input', False)

    if manual:
        step = context.user_data.get('step', 'team1')
        if step == 'team1':
            context.user_data['team1'] = text
            await update.message.reply_text("Now type the name of the second team:")
            context.user_data['step'] = 'team2'
            return ENTER_TEAM2
    else:
        # Scheduled game selection by number
        if text.isdigit():
            game_index = int(text) - 1
            games = context.user_data.get('games', [])
            if 0 <= game_index < len(games):
                game = games[game_index]
                context.user_data['selected_game'] = game
                # For scheduled games, go directly to choosing which team to analyze
                await update.message.reply_text(
                    f"✅ Selected: {game.away_team} @ {game.home_team}\n\n"
                    f"Which team do you want to analyze for betting?\n"
                    f"1️⃣ {game.away_team} (Away)\n"
                    f"2️⃣ {game.home_team} (Home)",
                    reply_markup=ReplyKeyboardMarkup([['1', '2']], one_time_keyboard=True, resize_keyboard=True)
                )
                return CHOOSE_BETTING_TEAM
            else:
                await update.message.reply_text("❌ Invalid number. Try again.")
                return ENTER_TEAM_NAMES
        else:
            await update.message.reply_text("❌ Invalid input. Use a number.")
            return ENTER_TEAM_NAMES

async def handle_team2_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    context.user_data['team2'] = text
    
    team1 = context.user_data['team1']
    team2 = text
    
    if team1.lower() == team2.lower():
        await update.message.reply_text("❌ Please enter two different teams.\n\nType the name of the second team:")
        return ENTER_TEAM2
    
    # Ask which team plays at home (only for manual entry)
    await update.message.reply_text(
        f"Which team plays at home?\n"
        f"1️⃣ {team1}\n"
        f"2️⃣ {team2}",
        reply_markup=ReplyKeyboardMarkup([['1', '2']], one_time_keyboard=True, resize_keyboard=True)
    )
    return CHOOSE_VENUE

async def handle_venue_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    team1 = context.user_data['team1']
    team2 = context.user_data['team2']
    
    if text == '1':
        context.user_data['home_team'] = team1
        context.user_data['venue_type'] = 'has_home_advantage'
    elif text == '2':
        context.user_data['home_team'] = team2
        context.user_data['venue_type'] = 'has_home_advantage'
    else:
        await update.message.reply_text("❌ Invalid option. Type 1 or 2.")
        return CHOOSE_VENUE
    
    return await ask_betting_team(update, context)

async def ask_betting_team(update: Update, context: ContextTypes.DEFAULT_TYPE):
    team1 = context.user_data['team1']
    team2 = context.user_data['team2']
    
    await update.message.reply_text(
        f"🎯 Which team do you want to analyze for betting?\n"
        f"1️⃣ {team1}\n"
        f"2️⃣ {team2}",
        reply_markup=ReplyKeyboardMarkup([['1', '2']], one_time_keyboard=True, resize_keyboard=True)
    )
    return CHOOSE_BETTING_TEAM

async def handle_betting_team_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    
    # Determine if it's a scheduled game or manual entry
    selected_game = context.user_data.get('selected_game')
    
    if selected_game:
        # Scheduled game: we already know who is home and away
        if text == '1':
            # Choose away team
            betting_team = selected_game.away_team
            opponent_team = selected_game.home_team
            venue = 'away'
        elif text == '2':
            # Choose home team
            betting_team = selected_game.home_team
            opponent_team = selected_game.away_team
            venue = 'home'
        else:
            await update.message.reply_text("❌ Invalid option. Type 1 or 2.")
            return CHOOSE_BETTING_TEAM
    else:
        # Manual entry: use established configuration
        team1 = context.user_data['team1']
        team2 = context.user_data['team2']
        home_team = context.user_data.get('home_team')
        
        if text == '1':
            betting_team = team1
            opponent_team = team2
        elif text == '2':
            betting_team = team2
            opponent_team = team1
        else:
            await update.message.reply_text("❌ Invalid option. Type 1 or 2.")
            return CHOOSE_BETTING_TEAM
        
        # Determine venue for manual entry
        if home_team == betting_team:
            venue = 'home'
        else:
            venue = 'away'    # Start background analysis immediately while providing user feedback
    await update.message.reply_text(f"🔍 Starting analysis for {betting_team}...")
    
    # Send immediate response to avoid webhook timeout
    progress_message = await update.message.reply_text("⏳ Step 1/3: Getting team statistics... (this may take 30-60 seconds)")
    
    # Create background task for the heavy operations
    async def perform_full_analysis():
        try:
            # Step 1: Get team stats
            await update.message.reply_text(f"📊 Step 2/3: Fetching detailed stats for {betting_team}...")
            team_stats = await chatbot.validate_and_get_team_stats_async(betting_team)
            
            if not team_stats:
                await update.message.reply_text(f"❌ Team '{betting_team}' not found or couldn't get its data.\n\n💡 Try using common names like 'Lakers', 'Warriors', 'Celtics', etc.\n\nUse /start to try again.")
                return None
            
            await update.message.reply_text(f"✅ Found: {team_stats.team_name}")
            
            # Step 2: Perform analysis
            await update.message.reply_text("🧠 Step 3/3: Running expert analysis and Bayesian evaluation...")
            analysis = await chatbot.perform_analysis_async(team_stats, opponent_team, venue)
            
            return team_stats, analysis
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error during analysis: {str(e)}\n\nPlease try again with /start")
            return None
    
    # Create the background task
    analysis_task = asyncio.create_task(perform_full_analysis())
    
    # Wait for the task to complete and get results
    result = await analysis_task
    if result is None:
        return ConversationHandler.END
    
    team_stats, analysis = result
    
    if analysis:
        # Create message using the same format as display_analysis_results
        message = await format_analysis_message(team_stats, opponent_team, venue, analysis)
        
        # Split message if it's too long for Telegram (4096 character limit)
        await send_long_message(update, message)
        
        # Ask if they want to continue with another analysis
        await update.message.reply_text(
            "Do you want to perform another analysis?\n"
            "1️⃣ Yes, another analysis\n"
            "2️⃣ No, finish",
            reply_markup=ReplyKeyboardMarkup([['1', '2']], one_time_keyboard=True, resize_keyboard=True)
        )
        return CONTINUE_OR_END
    else:
        await update.message.reply_text("❌ Could not perform analysis. Try again with /start.")
        return ConversationHandler.END

async def send_long_message(update: Update, message: str, max_length: int = 4000):
    """Split and send long messages that exceed Telegram's character limit"""
    if len(message) <= max_length:
        await update.message.reply_text(message, parse_mode='Markdown')
        return
    
    # Split the message into chunks
    lines = message.split('\n')
    current_chunk = ""
    
    for line in lines:
        # Check if adding this line would exceed the limit
        if len(current_chunk + line + '\n') > max_length:
            # Send current chunk if it's not empty
            if current_chunk.strip():
                await update.message.reply_text(current_chunk.strip(), parse_mode='Markdown')
            current_chunk = line + '\n'
        else:
            current_chunk += line + '\n'
    
    # Send the remaining chunk
    if current_chunk.strip():
        await update.message.reply_text(current_chunk.strip(), parse_mode='Markdown')

async def format_analysis_message(team_stats, opponent_name, venue, analysis):
    """Formats the analysis message similar to the chatbot's display_analysis_results"""
    
    # Generate summary reasons using the chatbot method
    summary_reasons = chatbot._generate_summary_reasons(analysis, team_stats, venue, opponent_name)
    
    message = "🎯 *ANALYSIS RESULTS*\n"
    message += "=" * 50 + "\n\n"
    
    # Team information
    message += f"📊 *TEAM INFORMATION: {team_stats.team_name}*\n"
    message += f"Record: {team_stats.wins}-{team_stats.losses} ({team_stats.win_percentage:.1%})\n"
    
    if hasattr(team_stats, 'last_10_games') and team_stats.last_10_games:
        message += f"Last 10 games: {team_stats.last_10_games}\n"
    
    if hasattr(team_stats, 'streak') and team_stats.streak:
        message += f"Current streak: {team_stats.streak}\n"
    
    message += f"Scoring: {team_stats.points_per_game:.1f} PPG\n"
    message += f"Defense: {team_stats.opponent_points_per_game:.1f} points allowed\n"
    
    if hasattr(team_stats, 'home_record') and team_stats.home_record:
        message += f"Home record: {team_stats.home_record}\n"
    
    if hasattr(team_stats, 'away_record') and team_stats.away_record:
        message += f"Away record: {team_stats.away_record}\n"
    
    if team_stats.unavailable_players:
        message += f"Unavailable players: {', '.join(team_stats.unavailable_players)}\n"
    else:
        message += "Unavailable players: None reported\n"
    
    message += f"Playing: {venue.upper()} vs {opponent_name}\n\n"
    
    # Main recommendation
    message += "🎯 *RECOMMENDATION*\n"
    rec_emoji = "✅" if analysis.recommendation == "safe" else "⚠️"
    message += f"{rec_emoji} *{analysis.recommendation.upper()} BET*\n"
    message += f"Risk Level: *{analysis.risk_level.upper()}*\n"
    message += f"Confidence: *{analysis.confidence:.1%}*\n\n"
    
    # Expert system analysis
    message += "🧠 *EXPERT SYSTEM ANALYSIS*\n"
    if analysis.triggered_rules:
        message += "Activated rules:\n"
        for rule in analysis.triggered_rules:
            message += f"• {rule}\n"
    else:
        message += "No specific rules activated\n"
    
    if analysis.reasoning:
        message += "\nKey factors:\n"
        for reason in analysis.reasoning:
            message += f"• {reason}\n"
    
    message += "\n"
    
    # Bayesian analysis
    message += "📈 *BAYESIAN NETWORK ANALYSIS*\n"
    message += f"Probabilistic evaluation: {analysis.bayesian_probability:.1%} confidence\n\n"
    
    # Final summary
    risk_color = "🟢" if analysis.risk_level == "low" else "🟡" if analysis.risk_level == "medium" else "🔴"
    
    message += f"{risk_color} *SUMMARY:* This is a *{analysis.recommendation.upper()}* bet with *{analysis.risk_level.upper()}* risk\n"
    message += f"📋 *REASONING:* {summary_reasons}\n\n"
    
    if analysis.recommendation == "safe":
        message += "💡 The analysis suggests favorable conditions for this bet."
    else:
        message += "⚠️ The analysis suggests caution with this bet due to identified risk factors."
    return message

async def handle_continue_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    
    if text == '1':
        # User wants to do another analysis
        # Clear previous session data
        context.user_data.clear()
        
        await update.message.reply_text(
            "🏀 Perfect! Let's do another analysis.\n"
            "What would you like to do?\n"
            "1️⃣ View upcoming games\n"
            "2️⃣ Enter teams manually",
            reply_markup=ReplyKeyboardMarkup([['1', '2']], one_time_keyboard=True, resize_keyboard=True)
        )
        return CHOOSING_TEAMS
    elif text == '2':
        # User wants to finish
        await update.message.reply_text(
            "👋 Thanks for using the NBA Sports Betting Bot!\n"
            "Use /start when you want to do another analysis."
        )
        return ConversationHandler.END
    else:
        await update.message.reply_text("❌ Invalid option. Type 1 or 2.")
        return CONTINUE_OR_END

# Cancel
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Session cancelled. Use /start to begin again.")
    return ConversationHandler.END

# Error handler
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

def create_application():
    """Create and configure the application"""
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    if not TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")
    
    application = ApplicationBuilder().token(TOKEN).build()
    
    # Conversation handler
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
    
    application.add_handler(conv_handler)
    application.add_error_handler(error_handler)
    
    return application

# For production deployment (Render, Heroku, etc.)
def main():
    """Main function for production deployment"""
    from dotenv import load_dotenv
    
    load_dotenv()
    
    application = create_application()
    WEBHOOK_URL = os.getenv("WEBHOOK_URL")
    PORT = int(os.getenv("PORT", 8080))
    
    if WEBHOOK_URL:
        logger.info(f"Starting webhook on port {PORT}")
        logger.info(f"Webhook URL: {WEBHOOK_URL}")
        
        # Configure webhook
        application.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            webhook_url=WEBHOOK_URL,
            drop_pending_updates=True
        )
    else:
        logger.info("No WEBHOOK_URL found, starting with polling")
        application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
