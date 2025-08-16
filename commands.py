"""
Command system for Minecraft Bedrock Server
Handles console and in-game commands
"""

import logging
from typing import Dict, List, Any, Callable

logger = logging.getLogger(__name__)

class Command:
    """Base command class"""
    
    def __init__(self, name: str, description: str, usage: str, permission: str = "player"):
        self.name = name
        self.description = description
        self.usage = usage
        self.permission = permission
    
    async def execute(self, server, player, args: List[str]) -> bool:
        """Execute the command"""
        raise NotImplementedError

class StopCommand(Command):
    """Stop server command"""
    
    def __init__(self):
        super().__init__("stop", "Stop the server", "stop", "admin")
    
    async def execute(self, server, player, args: List[str]) -> bool:
        logger.info("Server shutdown requested")
        server.running = False
        return True

class SayCommand(Command):
    """Say command - broadcast message"""
    
    def __init__(self):
        super().__init__("say", "Broadcast a message", "say <message>", "admin")
    
    async def execute(self, server, player, args: List[str]) -> bool:
        if not args:
            logger.info("Usage: say <message>")
            return False
        
        message = " ".join(args)
        await server.broadcast_message(f"[Server] {message}")
        logger.info(f"Server: {message}")
        return True

class KickCommand(Command):
    """Kick player command"""
    
    def __init__(self):
        super().__init__("kick", "Kick a player", "kick <username> [reason]", "admin")
    
    async def execute(self, server, player, args: List[str]) -> bool:
        if not args:
            logger.info("Usage: kick <username> [reason]")
            return False
        
        username = args[0]
        reason = " ".join(args[1:]) if len(args) > 1 else "Kicked by server"
        
        for target_player in server.players.values():
            if target_player.username.lower() == username.lower():
                await server.remove_player(target_player)
                logger.info(f"Kicked player: {username} - {reason}")
                return True
        
        logger.info(f"Player not found: {username}")
        return False

class ListCommand(Command):
    """List players command"""
    
    def __init__(self):
        super().__init__("list", "List online players", "list", "player")
    
    async def execute(self, server, player, args: List[str]) -> bool:
        if server.players:
            player_list = ", ".join([p.username for p in server.players.values()])
            logger.info(f"Online players ({len(server.players)}): {player_list}")
        else:
            logger.info("No players online")
        return True

class HelpCommand(Command):
    """Help command"""
    
    def __init__(self):
        super().__init__("help", "Show help", "help [command]", "player")
    
    async def execute(self, server, player, args: List[str]) -> bool:
        if args:
            # Show help for specific command
            command_name = args[0].lower()
            if command_name in server.commands:
                cmd = server.commands[command_name]
                logger.info(f"Help for {cmd.name}:")
                logger.info(f"  Description: {cmd.description}")
                logger.info(f"  Usage: {cmd.usage}")
                logger.info(f"  Permission: {cmd.permission}")
            else:
                logger.info(f"Unknown command: {command_name}")
        else:
            # Show all commands
            logger.info("Available commands:")
            for cmd in server.commands.values():
                logger.info(f"  {cmd.name} - {cmd.description}")
            logger.info("Use 'help <command>' for detailed help")
        return True

class TimeCommand(Command):
    """Set time command"""
    
    def __init__(self):
        super().__init__("time", "Set world time", "time <day|night|noon|midnight|value>", "admin")
    
    async def execute(self, server, player, args: List[str]) -> bool:
        if not args:
            logger.info("Usage: time <day|night|noon|midnight|value>")
            return False
        
        time_arg = args[0].lower()
        
        if time_arg == "day":
            server.world.set_time(1000)
        elif time_arg == "night":
            server.world.set_time(13000)
        elif time_arg == "noon":
            server.world.set_time(6000)
        elif time_arg == "midnight":
            server.world.set_time(18000)
        else:
            try:
                time_value = int(time_arg)
                server.world.set_time(time_value)
            except ValueError:
                logger.info("Invalid time value. Use: day, night, noon, midnight, or a number (0-24000)")
                return False
        
        logger.info(f"Time set to: {server.world.get_time()}")
        return True

class WeatherCommand(Command):
    """Set weather command"""
    
    def __init__(self):
        super().__init__("weather", "Set weather", "weather <clear|rain|thunder>", "admin")
    
    async def execute(self, server, player, args: List[str]) -> bool:
        if not args:
            logger.info("Usage: weather <clear|rain|thunder>")
            return False
        
        weather_arg = args[0].lower()
        
        if weather_arg == "clear":
            server.world.set_weather(0)
        elif weather_arg == "rain":
            server.world.set_weather(1)
        elif weather_arg == "thunder":
            server.world.set_weather(2)
        else:
            logger.info("Invalid weather. Use: clear, rain, or thunder")
            return False
        
        logger.info(f"Weather set to: {weather_arg}")
        return True

class GamemodeCommand(Command):
    """Set gamemode command"""
    
    def __init__(self):
        super().__init__("gamemode", "Set gamemode", "gamemode <survival|creative|adventure|spectator> [player]", "admin")
    
    async def execute(self, server, player, args: List[str]) -> bool:
        if not args:
            logger.info("Usage: gamemode <survival|creative|adventure|spectator> [player]")
            return False
        
        gamemode_arg = args[0].lower()
        target_player = player
        
        if len(args) > 1:
            username = args[1]
            for p in server.players.values():
                if p.username.lower() == username.lower():
                    target_player = p
                    break
            else:
                logger.info(f"Player not found: {username}")
                return False
        
        gamemode_map = {
            "survival": 0,
            "creative": 1,
            "adventure": 2,
            "spectator": 3
        }
        
        if gamemode_arg not in gamemode_map:
            logger.info("Invalid gamemode. Use: survival, creative, adventure, or spectator")
            return False
        
        target_player.set_game_mode(gamemode_map[gamemode_arg])
        logger.info(f"Set {target_player.username}'s gamemode to {gamemode_arg}")
        return True

class CommandManager:
    """Manages server commands"""
    
    def __init__(self):
        self.commands: Dict[str, Command] = {}
        self.register_default_commands()
    
    def register_default_commands(self):
        """Register default server commands"""
        self.register_command(StopCommand())
        self.register_command(SayCommand())
        self.register_command(KickCommand())
        self.register_command(ListCommand())
        self.register_command(HelpCommand())
        self.register_command(TimeCommand())
        self.register_command(WeatherCommand())
        self.register_command(GamemodeCommand())
    
    def register_command(self, command: Command):
        """Register a new command"""
        self.commands[command.name.lower()] = command
        logger.debug(f"Registered command: {command.name}")
    
    async def execute_command(self, server, player, command_line: str) -> bool:
        """Execute a command"""
        parts = command_line.split()
        if not parts:
            return False
        
        command_name = parts[0].lower()
        args = parts[1:]
        
        if command_name not in self.commands:
            logger.info(f"Unknown command: {command_name}. Type 'help' for available commands.")
            return False
        
        command = self.commands[command_name]
        
        # Check permissions (simplified)
        if command.permission == "admin" and not player.is_op():
            logger.info("You don't have permission to use this command.")
            return False
        
        try:
            return await command.execute(server, player, args)
        except Exception as e:
            logger.error(f"Error executing command {command_name}: {e}")
            return False
    
    def get_command_list(self) -> List[str]:
        """Get list of available commands"""
        return list(self.commands.keys())