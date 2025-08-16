#!/usr/bin/env python3
"""
Minecraft Bedrock Edition Server
Main entry point for the server
"""

import asyncio
import logging
import sys
import threading
import time
from server import MinecraftServer

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

def main():
    """Main entry point for the Minecraft Bedrock server"""
    try:
        # Create and start the server
        server = MinecraftServer()
        
        # Start console thread for commands
        console_thread = threading.Thread(target=server.console_loop, daemon=True)
        console_thread.start()
        
        logger.info("Starting Minecraft Bedrock Server...")
        logger.info("Server will be available at 0.0.0.0:19132")
        logger.info("Type 'stop' in console to shutdown the server")
        
        # Run the server
        asyncio.run(server.start())
        
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()