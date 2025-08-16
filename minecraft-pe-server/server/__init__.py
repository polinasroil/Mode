# Minecraft PE Server - Основной модуль
# Автор: Minecraft PE Server Team
# Версия: 1.0.0

"""
Основной модуль Minecraft PE Server

Этот модуль содержит основную логику сервера Minecraft PE.
"""

from .main import MinecraftPEServer, Player, World

__version__ = "1.0.0"
__author__ = "Minecraft PE Server Team"

__all__ = [
    'MinecraftPEServer',
    'Player', 
    'World'
]