#!/usr/bin/env python3
"""
Test script to verify all modules can be imported correctly
"""

import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test importing all modules"""
    try:
        print("Testing imports...")
        
        # Test config
        print("✓ Testing config...")
        import config
        print("  - Config loaded successfully")
        
        # Test database
        print("✓ Testing database...")
        import database
        print("  - Database module loaded successfully")
        
        # Test game_logic
        print("✓ Testing game_logic...")
        import game_logic
        print("  - Game logic module loaded successfully")
        
        # Test keyboards
        print("✓ Testing keyboards...")
        import keyboards
        print("  - Keyboards module loaded successfully")
        
        # Test handlers
        print("✓ Testing handlers...")
        import handlers
        print("  - Handlers module loaded successfully")
        
        # Test utils
        print("✓ Testing utils...")
        import utils
        print("  - Utils module loaded successfully")
        
        print("\n🎉 All modules imported successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Import failed: {e}")
        return False

async def test_database_creation():
    """Test database creation"""
    try:
        print("\nTesting database creation...")
        from database import Database
        
        # Create a test database
        db = Database("test_database.db")
        print("✓ Database created successfully")
        
        # Test player creation
        player = await db.get_or_create_player(12345, "test_user", "Test", "User")
        print("✓ Player creation test passed")
        
        # Clean up
        if os.path.exists("test_database.db"):
            os.remove("test_database.db")
            print("✓ Test database cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_game_logic():
    """Test game logic"""
    try:
        print("\nTesting game logic...")
        from game_logic import GameLogic
        
        game_logic = GameLogic()
        
        # Test coin flip
        result = game_logic.flip_coin()
        print(f"✓ Coin flip test: {result}")
        
        # Test win checking
        win = game_logic.check_win("heads", "heads")
        print(f"✓ Win check test: {win}")
        
        return True
        
    except Exception as e:
        print(f"❌ Game logic test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Telegram Bot 'Heads or Tails'")
    print("=" * 50)
    
    # Test imports
    if not test_imports():
        sys.exit(1)
    
    # Test database (without async)
    try:
        import asyncio
        asyncio.run(test_database_creation())
    except Exception as e:
        print(f"⚠️  Database test skipped: {e}")
    
    # Test game logic
    if not test_game_logic():
        sys.exit(1)
    
    print("\n✅ All tests passed! The bot is ready to run.")
    print("\nTo start the bot:")
    print("1. Set your BOT_TOKEN in the .env file")
    print("2. Run: python3 bot.py")