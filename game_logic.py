import random
import asyncio
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import uuid

class GameLogic:
    def __init__(self):
        self.active_games: Dict[str, Dict[str, Any]] = {}
        self.active_duels: Dict[str, Dict[str, Any]] = {}
    
    def flip_coin(self) -> str:
        """Подбросить монету"""
        return random.choice(['heads', 'tails'])
    
    def check_win(self, player_choice: str, coin_result: str) -> bool:
        """Проверить, выиграл ли игрок"""
        return player_choice == coin_result
    
    def calculate_win_amount(self, bet: int) -> int:
        """Рассчитать сумму выигрыша"""
        return bet * 2
    
    def generate_duel_id(self) -> str:
        """Сгенерировать уникальный ID для дуэли"""
        return str(uuid.uuid4())[:8]
    
    async def start_bot_game(self, user_id: int, bet: int) -> Dict[str, Any]:
        """Начать игру с ботом"""
        game_id = f"bot_{user_id}_{int(datetime.now().timestamp())}"
        
        game_data = {
            'game_id': game_id,
            'user_id': user_id,
            'bet': bet,
            'game_type': 'bot',
            'status': 'waiting_choice',
            'created_at': datetime.now(),
            'expires_at': datetime.now() + timedelta(seconds=30)
        }
        
        self.active_games[game_id] = game_data
        return game_data
    
    async def make_bot_choice(self, game_id: str, player_choice: str) -> Dict[str, Any]:
        """Сделать выбор в игре с ботом"""
        if game_id not in self.active_games:
            return {'error': 'Игра не найдена'}
        
        game = self.active_games[game_id]
        
        if game['status'] != 'waiting_choice':
            return {'error': 'Неверный статус игры'}
        
        # Подбрасываем монету
        coin_result = self.flip_coin()
        
        # Проверяем результат
        player_won = self.check_win(player_choice, coin_result)
        win_amount = self.calculate_win_amount(game['bet']) if player_won else 0
        
        # Обновляем статус игры
        game['status'] = 'completed'
        game['player_choice'] = player_choice
        game['coin_result'] = coin_result
        game['player_won'] = player_won
        game['win_amount'] = win_amount
        game['completed_at'] = datetime.now()
        
        return {
            'game_id': game_id,
            'player_choice': player_choice,
            'coin_result': coin_result,
            'player_won': player_won,
            'win_amount': win_amount,
            'bet': game['bet']
        }
    
    async def create_duel(self, creator_id: int, opponent_id: int) -> Dict[str, Any]:
        """Создать дуэль"""
        duel_id = self.generate_duel_id()
        expires_at = datetime.now() + timedelta(seconds=60)
        
        duel_data = {
            'duel_id': duel_id,
            'creator_id': creator_id,
            'opponent_id': opponent_id,
            'status': 'pending',
            'created_at': datetime.now(),
            'expires_at': expires_at,
            'creator_bet': None,
            'opponent_bet': None,
            'creator_choice': None,
            'opponent_choice': None
        }
        
        self.active_duels[duel_id] = duel_data
        return duel_data
    
    async def accept_duel(self, duel_id: str, opponent_id: int) -> Dict[str, Any]:
        """Принять дуэль"""
        if duel_id not in self.active_duels:
            return {'error': 'Дуэль не найдена'}
        
        duel = self.active_duels[duel_id]
        
        if duel['opponent_id'] != opponent_id:
            return {'error': 'Вы не являетесь приглашенным игроком'}
        
        if duel['status'] != 'pending':
            return {'error': 'Дуэль уже не активна'}
        
        if datetime.now() > duel['expires_at']:
            return {'error': 'Время ожидания дуэли истекло'}
        
        duel['status'] = 'accepted'
        return duel
    
    async def set_duel_bet(self, duel_id: str, user_id: int, bet: int) -> Dict[str, Any]:
        """Установить ставку в дуэли"""
        if duel_id not in self.active_duels:
            return {'error': 'Дуэль не найдена'}
        
        duel = self.active_duels[duel_id]
        
        if user_id == duel['creator_id']:
            duel['creator_bet'] = bet
        elif user_id == duel['opponent_id']:
            duel['opponent_bet'] = bet
        else:
            return {'error': 'Вы не являетесь участником дуэли'}
        
        # Проверяем, готовы ли оба игрока
        if duel['creator_bet'] is not None and duel['opponent_bet'] is not None:
            duel['status'] = 'waiting_choices'
        
        return duel
    
    async def set_duel_choice(self, duel_id: str, user_id: int, choice: str) -> Dict[str, Any]:
        """Установить выбор в дуэли"""
        if duel_id not in self.active_duels:
            return {'error': 'Дуэль не найдена'}
        
        duel = self.active_duels[duel_id]
        
        if user_id == duel['creator_id']:
            duel['creator_choice'] = choice
        elif user_id == duel['opponent_id']:
            duel['opponent_choice'] = choice
        else:
            return {'error': 'Вы не являетесь участником дуэли'}
        
        # Проверяем, готовы ли оба игрока
        if duel['creator_choice'] is not None and duel['opponent_choice'] is not None:
            return await self.complete_duel(duel_id)
        
        return duel
    
    async def complete_duel(self, duel_id: str) -> Dict[str, Any]:
        """Завершить дуэль"""
        if duel_id not in self.active_duels:
            return {'error': 'Дуэль не найдена'}
        
        duel = self.active_duels[duel_id]
        
        # Подбрасываем монету
        coin_result = self.flip_coin()
        
        # Проверяем результаты
        creator_won = self.check_win(duel['creator_choice'], coin_result)
        opponent_won = self.check_win(duel['opponent_choice'], coin_result)
        
        # Определяем победителя
        if creator_won and not opponent_won:
            winner_id = duel['creator_id']
            winner_bet = duel['creator_bet']
            loser_bet = duel['opponent_bet']
            result = 'creator_won'
        elif opponent_won and not creator_won:
            winner_id = duel['opponent_id']
            winner_bet = duel['opponent_bet']
            loser_bet = duel['creator_bet']
            result = 'opponent_won'
        else:
            # Ничья - оба угадали или оба не угадали
            winner_id = None
            winner_bet = 0
            loser_bet = 0
            result = 'draw'
        
        # Обновляем статус дуэли
        duel['status'] = 'completed'
        duel['coin_result'] = coin_result
        duel['winner_id'] = winner_id
        duel['winner_bet'] = winner_bet
        duel['loser_bet'] = loser_bet
        duel['result'] = result
        duel['completed_at'] = datetime.now()
        
        return {
            'duel_id': duel_id,
            'coin_result': coin_result,
            'creator_choice': duel['creator_choice'],
            'opponent_choice': duel['opponent_choice'],
            'creator_won': creator_won,
            'opponent_won': opponent_won,
            'winner_id': winner_id,
            'winner_bet': winner_bet,
            'loser_bet': loser_bet,
            'result': result,
            'creator_bet': duel['creator_bet'],
            'opponent_bet': duel['opponent_bet']
        }
    
    async def get_active_game(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Получить активную игру пользователя"""
        for game in self.active_games.values():
            if game['user_id'] == user_id and game['status'] in ['waiting_choice', 'waiting_bet']:
                return game
        return None
    
    async def get_active_duel(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Получить активную дуэль пользователя"""
        for duel in self.active_duels.values():
            if (duel['creator_id'] == user_id or duel['opponent_id'] == user_id) and \
               duel['status'] in ['pending', 'accepted', 'waiting_choices']:
                return duel
        return None
    
    async def cleanup_expired_games(self) -> int:
        """Очистить истекшие игры"""
        current_time = datetime.now()
        expired_games = []
        
        for game_id, game in self.active_games.items():
            if game['status'] == 'waiting_choice' and current_time > game['expires_at']:
                expired_games.append(game_id)
        
        for game_id in expired_games:
            del self.active_games[game_id]
        
        return len(expired_games)
    
    async def cleanup_expired_duels(self) -> int:
        """Очистить истекшие дуэли"""
        current_time = datetime.now()
        expired_duels = []
        
        for duel_id, duel in self.active_duels.items():
            if duel['status'] == 'pending' and current_time > duel['expires_at']:
                expired_duels.append(duel_id)
        
        for duel_id in expired_duels:
            del self.active_duels[duel_id]
        
        return len(expired_duels)
    
    def get_coin_animation(self) -> str:
        """Получить анимацию подбрасывания монеты"""
        animations = [
            "🪙 Монета крутится...",
            "🪙 Монета летит в воздухе...",
            "🪙 Монета падает...",
            "🪙 Монета приземляется..."
        ]
        return random.choice(animations)
    
    def get_win_message(self, amount: int) -> str:
        """Получить сообщение о выигрыше"""
        messages = [
            f"🎉 Поздравляем! Вы выиграли {amount}!",
            f"🏆 Отличная игра! Выигрыш: {amount}",
            f"🔥 Невероятно! Вы получили {amount}!",
            f"🚀 Победа! Ваш выигрыш: {amount}"
        ]
        return random.choice(messages)
    
    def get_lose_message(self, amount: int) -> str:
        """Получить сообщение о проигрыше"""
        messages = [
            f"😔 К сожалению, вы проиграли {amount}.",
            f"💔 Не повезло в этот раз. Потеря: {amount}",
            f"😅 Попробуйте еще раз! Потеря: {amount}",
            f"🤞 В следующий раз повезет! Потеря: {amount}"
        ]
        return random.choice(messages)