#!/usr/bin/env python3
"""
Simple server launcher
"""

import subprocess
import sys
import os

def main():
    print("🎮 Minecraft Bedrock Server")
    print("=" * 40)
    print("Starting server...")
    print()
    
    try:
        # Run the main server
        subprocess.run([sys.executable, "main.py"])
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()