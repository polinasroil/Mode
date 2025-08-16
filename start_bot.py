#!/usr/bin/env python3
"""
Startup script for Telegram Bot "Heads or Tails"
Handles environment setup and bot launching
"""

import os
import sys
import logging
import asyncio
from pathlib import Path

def setup_environment():
    """Setup environment and check requirements"""
    print("🚀 Starting Telegram Bot 'Heads or Tails'")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8+ is required")
        print(f"   Current version: {sys.version}")
        sys.exit(1)
    
    print(f"✓ Python version: {sys.version.split()[0]}")
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("❌ Error: .env file not found")
        print("   Please copy .env.example to .env and configure your bot token")
        sys.exit(1)
    
    print("✓ Environment file found")
    
    # Check if virtual environment is activated
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Warning: Virtual environment not detected")
        print("   It's recommended to use a virtual environment")
    else:
        print("✓ Virtual environment detected")
    
    return True

def setup_logging():
    """Setup logging configuration"""
    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "bot.log", encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Logging setup completed")
    return logger

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("\n📦 Checking dependencies...")
    
    required_modules = [
        'aiogram',
        'dotenv',
        'sqlite3'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✓ {module}")
        except ImportError:
            print(f"❌ {module} - missing")
            missing_modules.append(module)
    
    if missing_modules:
        print(f"\n❌ Missing dependencies: {', '.join(missing_modules)}")
        print("   Please install them with: pip install -r requirements.txt")
        return False
    
    print("✓ All dependencies found")
    return True

def check_configuration():
    """Check bot configuration"""
    print("\n⚙️  Checking configuration...")
    
    try:
        from config import BOT_TOKEN
        
        if not BOT_TOKEN or BOT_TOKEN == "your_bot_token_here":
            print("❌ Bot token not configured")
            print("   Please set your BOT_TOKEN in the .env file")
            return False
        
        print("✓ Bot token configured")
        
        # Test database connection
        from database import Database
        db = Database()
        print("✓ Database connection successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

async def start_bot():
    """Start the bot"""
    print("\n🤖 Starting bot...")
    
    try:
        # Import and start the bot
        from bot import main
        
        logger = logging.getLogger(__name__)
        logger.info("Bot startup initiated")
        
        await main()
        
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
        logger.info("Bot stopped by user")
    except Exception as e:
        print(f"\n❌ Bot error: {e}")
        logger.error(f"Bot error: {e}")
        sys.exit(1)

def main():
    """Main startup function"""
    try:
        # Setup environment
        if not setup_environment():
            sys.exit(1)
        
        # Setup logging
        logger = setup_logging()
        
        # Check dependencies
        if not check_dependencies():
            sys.exit(1)
        
        # Check configuration
        if not check_configuration():
            sys.exit(1)
        
        # Start the bot
        print("\n🎮 Bot is ready to start!")
        print("Press Ctrl+C to stop the bot")
        print("=" * 50)
        
        asyncio.run(start_bot())
        
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Startup error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()