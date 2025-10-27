import sqlite3
import asyncio
from typing import Optional, Tuple, Dict, Any
from datetime import datetime
import json

class Database:
    def __init__(self, db_path: str = "game_database.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Инициализация базы данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Таблица игроков
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS players (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                balance INTEGER DEFAULT 1000,
                wins INTEGER DEFAULT 0,
                losses INTEGER DEFAULT 0,
                total_games INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица дуэлей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS duels (
                duel_id TEXT PRIMARY KEY,
                creator_id INTEGER,
                opponent_id INTEGER,
                creator_bet INTEGER,
                opponent_bet INTEGER,
                creator_choice TEXT,
                opponent_choice TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                result TEXT,
                winner_id INTEGER
            )
        ''')
        
        # Таблица игр
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS games (
                game_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                game_type TEXT,
                bet INTEGER,
                choice TEXT,
                result TEXT,
                win_amount INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    async def get_or_create_player(self, user_id: int, username: str = None, 
                                 first_name: str = None, last_name: str = None) -> Dict[str, Any]:
        """Получить или создать игрока"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM players WHERE user_id = ?
        ''', (user_id,))
        
        player = cursor.fetchone()
        
        if player is None:
            # Создаем нового игрока
            cursor.execute('''
                INSERT INTO players (user_id, username, first_name, last_name, balance)
                VALUES (?, ?, ?, ?, 1000)
            ''', (user_id, username, first_name, last_name))
            
            conn.commit()
            
            return {
                'user_id': user_id,
                'username': username,
                'first_name': first_name,
                'last_name': last_name,
                'balance': 1000,
                'wins': 0,
                'losses': 0,
                'total_games': 0
            }
        else:
            # Обновляем время последней активности
            cursor.execute('''
                UPDATE players SET last_activity = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', (user_id,))
            
            conn.commit()
            
            return {
                'user_id': player[0],
                'username': player[1],
                'first_name': player[2],
                'last_name': player[3],
                'balance': player[4],
                'wins': player[5],
                'losses': player[6],
                'total_games': player[7]
            }
        
        conn.close()
    
    async def update_balance(self, user_id: int, amount: int) -> bool:
        """Обновить баланс игрока"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE players SET balance = balance + ? WHERE user_id = ?
        ''', (amount, user_id))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    async def record_game_result(self, user_id: int, game_type: str, bet: int, 
                               choice: str, result: str, win_amount: int) -> bool:
        """Записать результат игры"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Записываем игру
        cursor.execute('''
            INSERT INTO games (user_id, game_type, bet, choice, result, win_amount)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, game_type, bet, choice, result, win_amount))
        
        # Обновляем статистику игрока
        if result == 'win':
            cursor.execute('''
                UPDATE players 
                SET wins = wins + 1, total_games = total_games + 1
                WHERE user_id = ?
            ''', (user_id,))
        else:
            cursor.execute('''
                UPDATE players 
                SET losses = losses + 1, total_games = total_games + 1
                WHERE user_id = ?
            ''', (user_id,))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    async def create_duel(self, duel_id: str, creator_id: int, opponent_id: int, 
                         expires_at: datetime) -> bool:
        """Создать дуэль"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO duels (duel_id, creator_id, opponent_id, expires_at)
            VALUES (?, ?, ?, ?)
        ''', (duel_id, creator_id, opponent_id, expires_at))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    async def get_duel(self, duel_id: str) -> Optional[Dict[str, Any]]:
        """Получить информацию о дуэли"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM duels WHERE duel_id = ?
        ''', (duel_id,))
        
        duel = cursor.fetchone()
        conn.close()
        
        if duel:
            return {
                'duel_id': duel[0],
                'creator_id': duel[1],
                'opponent_id': duel[2],
                'creator_bet': duel[3],
                'opponent_bet': duel[4],
                'creator_choice': duel[5],
                'opponent_choice': duel[6],
                'status': duel[7],
                'created_at': duel[8],
                'expires_at': duel[9],
                'result': duel[10],
                'winner_id': duel[11]
            }
        
        return None
    
    async def update_duel_bet(self, duel_id: str, user_id: int, bet: int) -> bool:
        """Обновить ставку в дуэли"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Определяем, чью ставку обновляем
        cursor.execute('''
            SELECT creator_id, opponent_id FROM duels WHERE duel_id = ?
        ''', (duel_id,))
        
        duel = cursor.fetchone()
        if not duel:
            conn.close()
            return False
        
        creator_id, opponent_id = duel
        
        if user_id == creator_id:
            cursor.execute('''
                UPDATE duels SET creator_bet = ? WHERE duel_id = ?
            ''', (bet, duel_id))
        elif user_id == opponent_id:
            cursor.execute('''
                UPDATE duels SET opponent_bet = ? WHERE duel_id = ?
            ''', (bet, duel_id))
        else:
            conn.close()
            return False
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    async def update_duel_choice(self, duel_id: str, user_id: int, choice: str) -> bool:
        """Обновить выбор в дуэли"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Определяем, чей выбор обновляем
        cursor.execute('''
            SELECT creator_id, opponent_id FROM duels WHERE duel_id = ?
        ''', (duel_id,))
        
        duel = cursor.fetchone()
        if not duel:
            conn.close()
            return False
        
        creator_id, opponent_id = duel
        
        if user_id == creator_id:
            cursor.execute('''
                UPDATE duels SET creator_choice = ? WHERE duel_id = ?
            ''', (choice, duel_id))
        elif user_id == opponent_id:
            cursor.execute('''
                UPDATE duels SET opponent_choice = ? WHERE duel_id = ?
            ''', (choice, duel_id))
        else:
            conn.close()
            return False
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    async def complete_duel(self, duel_id: str, result: str, winner_id: int) -> bool:
        """Завершить дуэль"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE duels SET status = 'completed', result = ?, winner_id = ?
            WHERE duel_id = ?
        ''', (result, winner_id, duel_id))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    async def get_player_stats(self, user_id: int) -> Dict[str, Any]:
        """Получить статистику игрока"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT balance, wins, losses, total_games FROM players WHERE user_id = ?
        ''', (user_id,))
        
        stats = cursor.fetchone()
        conn.close()
        
        if stats:
            balance, wins, losses, total_games = stats
            win_rate = (wins / total_games * 100) if total_games > 0 else 0
            
            return {
                'balance': balance,
                'wins': wins,
                'losses': losses,
                'total_games': total_games,
                'win_rate': round(win_rate, 1)
            }
        
        return None
    
    async def cleanup_expired_duels(self) -> int:
        """Очистить истекшие дуэли"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM duels 
            WHERE status = 'pending' AND expires_at < CURRENT_TIMESTAMP
        ''')
        
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        return deleted_count