#!/usr/bin/env python3
"""
Minecraft Bedrock Server - Main Entry Point
Fully functional server with protocol compatibility
"""

import asyncio
import logging
import signal
import sys
import threading
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('server.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Import server components
try:
    from compatible_server import CompatibleServer
    from server import MinecraftServer
except ImportError as e:
    logger.error(f"Failed to import server modules: {e}")
    sys.exit(1)

class ServerManager:
    """Manages server lifecycle and console commands"""
    
    def __init__(self):
        self.server = None
        self.running = False
        self.console_thread = None
        
    async def start_server(self, use_compatible=True):
        """Start the server"""
        try:
            if use_compatible:
                logger.info("Starting compatible server...")
                self.server = CompatibleServer()
            else:
                logger.info("Starting main server...")
                self.server = MinecraftServer()
            
            # Start console thread
            self.console_thread = threading.Thread(target=self.console_loop, daemon=True)
            self.console_thread.start()
            
            # Start server
            await self.server.start()
            
        except Exception as e:
            logger.error(f"Failed to start server: {e}")
            raise
    
    def console_loop(self):
        """Console command loop"""
        logger.info("Console ready. Type 'help' for commands.")
        
        while self.running:
            try:
                command = input("> ").strip().lower()
                
                if command == "stop":
                    logger.info("Shutdown requested via console")
                    self.running = False
                    break
                elif command == "help":
                    self.show_help()
                elif command == "status":
                    self.show_status()
                elif command == "players":
                    self.show_players()
                elif command.startswith("say "):
                    message = command[4:]
                    self.broadcast_message(message)
                elif command == "save":
                    self.save_world()
                elif command == "restart":
                    logger.info("Restart requested")
                    self.running = False
                    break
                else:
                    logger.info(f"Unknown command: {command}. Type 'help' for available commands.")
                    
            except (EOFError, KeyboardInterrupt):
                logger.info("Console interrupted")
                self.running = False
                break
            except Exception as e:
                logger.error(f"Console error: {e}")
    
    def show_help(self):
        """Show available commands"""
        help_text = """
Available commands:
  help     - Show this help
  status   - Show server status
  players  - Show connected players
  say <msg> - Broadcast message to players
  save     - Save world data
  restart  - Restart server
  stop     - Stop server
        """
        logger.info(help_text)
    
    def show_status(self):
        """Show server status"""
        if self.server:
            status = f"""
Server Status:
  Running: {self.running}
  Players: {len(self.server.players) if hasattr(self.server, 'players') else 0}
  Uptime: {time.time() - getattr(self.server, 'start_time', time.time()):.1f}s
            """
            logger.info(status)
        else:
            logger.info("Server not running")
    
    def show_players(self):
        """Show connected players"""
        if self.server and hasattr(self.server, 'players'):
            if self.server.players:
                players = [player.username for player in self.server.players.values()]
                logger.info(f"Connected players: {', '.join(players)}")
            else:
                logger.info("No players connected")
        else:
            logger.info("Server not running")
    
    def broadcast_message(self, message):
        """Broadcast message to players"""
        if self.server and hasattr(self.server, 'broadcast_message'):
            asyncio.create_task(self.server.broadcast_message(f"[Server] {message}"))
            logger.info(f"Broadcast: {message}")
        else:
            logger.info("Cannot broadcast - server not ready")
    
    def save_world(self):
        """Save world data"""
        if self.server and hasattr(self.server, 'world'):
            asyncio.create_task(self.server.world.save())
            logger.info("World saved")
        else:
            logger.info("Cannot save - world not available")

async def main():
    """Main function"""
    print("=" * 60)
    print("🎮 MINECRAFT BEDROCK SERVER")
    print("=" * 60)
    print("Starting server...")
    print()
    
    manager = ServerManager()
    manager.running = True
    
    try:
        # Start server with compatible version
        await manager.start_server(use_compatible=True)
        
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server error: {e}")
    finally:
        manager.running = False
        if manager.server:
            await manager.server.shutdown()
        logger.info("Server shutdown complete")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)