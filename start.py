"""
NBA Sports Betting Expert - Startup Script
Choose between web interface or Telegram bot
"""

import sys
import os
from dotenv import load_dotenv

def main():
    # Load environment variables
    load_dotenv()
    
    print("🏀 NBA Sports Betting Expert System")
    print("=" * 50)
    print()
    print("Choose how you want to run the chatbot:")
    print("1. 🌐 Web Interface (Beautiful chat UI)")
    print("2. 📱 Telegram Bot (Webhook mode)")
    print("3. 📱 Telegram Bot (Polling mode)")
    print("4. ❓ Help")
    print()
    
    while True:
        choice = input("Enter your choice (1-4): ").strip()
        
        if choice == "1":
            run_web_interface()
            break
        elif choice == "2":
            run_telegram_webhook()
            break
        elif choice == "3":
            run_telegram_polling()
            break
        elif choice == "4":
            show_help()
        else:
            print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")

def run_web_interface():
    """Run the web interface"""
    print("\n🌐 Starting NBA Betting Expert Web Interface...")
    print("📍 The chatbot will be available at: http://localhost:5000")
    print("⏹️  Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        from web_server import app
        app.run(debug=False, host='0.0.0.0', port=5000)
    except ImportError as e:
        print(f"❌ Error importing web server: {e}")
        print("Make sure Flask is installed: pip install flask flask-cors")
    except Exception as e:
        print(f"❌ Error starting web server: {e}")

def run_telegram_webhook():
    """Run Telegram bot in webhook mode"""
    webhook_url = os.getenv("WEBHOOK_URL")
    
    if not webhook_url:
        print("❌ WEBHOOK_URL not found in environment variables.")
        print("Please set WEBHOOK_URL in your .env file for webhook mode.")
        print("Example: WEBHOOK_URL=https://your-app.onrender.com")
        return
    
    print(f"\n📱 Starting Telegram Bot (Webhook Mode)...")
    print(f"🔗 Webhook URL: {webhook_url}")
    print("⏹️  Press Ctrl+C to stop")
    print("-" * 50)
    
    try:
        from app import app
        port = int(os.getenv("PORT", 8080))
        app.run(host="0.0.0.0", port=port)
    except ImportError as e:
        print(f"❌ Error importing webhook app: {e}")
        print("Make sure Quart is installed: pip install quart")
    except Exception as e:
        print(f"❌ Error starting webhook: {e}")

def run_telegram_polling():
    """Run Telegram bot in polling mode"""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not token:
        print("❌ TELEGRAM_BOT_TOKEN not found in environment variables.")
        print("Please set your Telegram bot token in the .env file.")
        return
    
    print(f"\n📱 Starting Telegram Bot (Polling Mode)...")
    print("🔄 Bot will check for messages every few seconds")
    print("⏹️  Press Ctrl+C to stop")
    print("-" * 50)
    
    try:
        from telegram_bot import main as telegram_main
        telegram_main()
    except ImportError as e:
        print(f"❌ Error importing Telegram bot: {e}")
        print("Make sure python-telegram-bot is installed")
    except Exception as e:
        print(f"❌ Error starting Telegram bot: {e}")

def show_help():
    """Show help information"""
    print("\n❓ Help - NBA Sports Betting Expert")
    print("=" * 50)
    print()
    print("🌐 Web Interface:")
    print("   • Beautiful chat interface accessible via web browser")
    print("   • Real-time messaging with the NBA AI expert")
    print("   • No setup required, just run and open localhost:5000")
    print()
    print("📱 Telegram Bot (Webhook):")
    print("   • For production deployment (e.g., Render, Heroku)")
    print("   • Requires WEBHOOK_URL environment variable")
    print("   • Faster response times, better for high traffic")
    print()
    print("📱 Telegram Bot (Polling):")
    print("   • For local development and testing")
    print("   • Requires TELEGRAM_BOT_TOKEN environment variable")
    print("   • Bot checks for messages periodically")
    print()
    print("🔧 Environment Variables (.env file):")
    print("   TELEGRAM_BOT_TOKEN=your_bot_token_here")
    print("   WEBHOOK_URL=https://your-app.onrender.com")
    print("   PORT=8080")
    print()
    print("💡 Recommendation:")
    print("   • Use Web Interface for the best user experience")
    print("   • Use Telegram Bot for mobile messaging")
    print()

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'requests', 'pandas', 'numpy', 'nba_api', 
        'experta', 'pgmpy', 'networkx', 'scikit-learn'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("⚠️  Missing required packages:")
        for package in missing_packages:
            print(f"   • {package}")
        print()
        print("📦 Install missing packages with:")
        print("   pip install -r requirements.txt")
        print()
        return False
    
    return True

if __name__ == "__main__":
    print("🔍 Checking dependencies...")
    
    if not check_dependencies():
        print("❌ Please install missing dependencies first.")
        sys.exit(1)
    
    print("✅ All dependencies found!")
    print()
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Thanks for using NBA Betting Expert!")
        print("🏀 Come back anytime for NBA analysis!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
