import os
import asyncio
from quart import Quart, request, Response
from telegram import Update
from telegram_bot import create_application

# Create Quart app
app = Quart(__name__)

# Create telegram application
telegram_app = create_application()

@app.route("/webhook", methods=["POST"])
async def webhook():
    """Handle incoming webhook requests from Telegram"""
    try:
        # Get the request data
        data = await request.get_json()
        
        if data:
            # Create Update object
            update = Update.de_json(data, telegram_app.bot)
            
            # Process the update
            await telegram_app.process_update(update)
        
        return Response("OK", status=200)
    except Exception as e:
        print(f"Error processing webhook: {e}")
        return Response("Error", status=500)

@app.route("/health", methods=["GET"])
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "NBA Betting Bot"}

@app.route("/", methods=["GET"])
async def home():
    """Root endpoint"""
    return {"message": "NBA Sports Betting Bot is running!", "status": "active"}

async def setup_webhook():
    """Set up the webhook URL with Telegram"""
    try:
        webhook_url = os.getenv("WEBHOOK_URL")
        if webhook_url:
            if not webhook_url.endswith("/webhook"):
                webhook_url += "/webhook"
            
            await telegram_app.bot.set_webhook(url=webhook_url)
            print(f"✅ Webhook set successfully: {webhook_url}")
        else:
            print("❌ No WEBHOOK_URL environment variable found")
    except Exception as e:
        print(f"❌ Failed to set webhook: {e}")

@app.before_serving
async def startup():
    """Initialize the application"""
    print("🚀 Starting NBA Sports Betting Bot...")
    await telegram_app.initialize()
    await setup_webhook()
    print("✅ Bot initialized successfully")

@app.after_serving
async def shutdown():
    """Cleanup on shutdown"""
    print("🛑 Shutting down bot...")
    await telegram_app.shutdown()

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
