import re
from typing import Dict, Any, Optional
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import MESSAGES, MIN_BET, MAX_BET
from database import Database
from game_logic import GameLogic
from keyboards import *

class TextStates(StatesGroup):
    waiting_for_custom_bet = State()
    waiting_for_duel_opponent = State()

class TextHandlers:
    def __init__(self, db: Database, game_logic: GameLogic):
        self.db = db
        self.game_logic = game_logic
    
    async def handle_text_message(self, message: types.Message, user_states: Dict[int, Dict[str, Any]]) -> bool:
        """Обработчик текстовых сообщений"""
        text = message.text.strip()
        user_id = message.from_user.id
        
        # Проверяем, есть ли активное состояние у пользователя
        if user_id in user_states:
            state = user_states[user_id]
            
            # Обработка кастомной ставки
            if 'waiting_bet' in state:
                return await self.handle_custom_bet(message, user_states)
            
            # Обработка ввода соперника для дуэли
            if 'waiting_opponent' in state:
                return await self.handle_duel_opponent(message, user_states)
        
        # Обработка команд
        if text.lower() in ['/start', 'start', 'начать', 'играть']:
            await self.handle_start_command(message)
            return True
        
        if text.lower() in ['/help', 'help', 'помощь', 'правила']:
            await self.handle_help_command(message)
            return True
        
        if text.lower() in ['/stats', 'stats', 'статистика']:
            await self.handle_stats_command(message)
            return True
        
        if text.lower() in ['/balance', 'balance', 'баланс']:
            await self.handle_balance_command(message)
            return True
        
        # Обработка быстрых команд
        if text.lower() in ['орёл', 'орел', 'heads']:
            return await self.handle_quick_choice(message, 'heads', user_states)
        
        if text.lower() in ['решка', 'tails']:
            return await self.handle_quick_choice(message, 'tails', user_states)
        
        # Обработка числовых ставок
        if text.isdigit():
            bet = int(text)
            if MIN_BET <= bet <= MAX_BET:
                return await self.handle_quick_bet(message, bet, user_states)
        
        return False
    
    async def handle_custom_bet(self, message: types.Message, user_states: Dict[int, Dict[str, Any]]) -> bool:
        """Обработка кастомной ставки"""
        text = message.text.strip()
        user_id = message.from_user.id
        
        if not text.isdigit():
            await message.answer(
                f"❌ Пожалуйста, введите число от {MIN_BET} до {MAX_BET}",
                reply_markup=get_cancel_keyboard()
            )
            return True
        
        bet = int(text)
        
        if bet < MIN_BET or bet > MAX_BET:
            await message.answer(
                f"❌ Ставка должна быть от {MIN_BET} до {MAX_BET}",
                reply_markup=get_cancel_keyboard()
            )
            return True
        
        # Проверяем баланс
        stats = await self.db.get_player_stats(user_id)
        if not stats or stats['balance'] < bet:
            await message.answer(
                MESSAGES['not_enough_balance'].format(balance=stats['balance'] if stats else 0),
                reply_markup=get_balance_keyboard()
            )
            return True
        
        # Создаем игру
        game_data = await self.game_logic.start_bot_game(user_id, bet)
        
        # Обновляем состояние
        user_states[user_id] = {
            'game_id': game_data['game_id'],
            'bet': bet,
            'game_type': 'bot'
        }
        
        # Показываем выбор стороны монеты
        await message.answer(
            MESSAGES['choose_side'],
            reply_markup=get_coin_choice_keyboard()
        )
        
        return True
    
    async def handle_duel_opponent(self, message: types.Message, user_states: Dict[int, Dict[str, Any]]) -> bool:
        """Обработка ввода соперника для дуэли"""
        text = message.text.strip()
        user_id = message.from_user.id
        
        # Извлекаем ID пользователя из текста (может быть @username или ID)
        opponent_id = None
        
        if text.startswith('@'):
            # Это username
            username = text[1:]
            # Здесь нужно будет добавить логику поиска пользователя по username
            await message.answer(
                "❌ Поиск по username пока не поддерживается. Используйте ID пользователя.",
                reply_markup=get_cancel_keyboard()
            )
            return True
        
        elif text.isdigit():
            opponent_id = int(text)
        else:
            await message.answer(
                "❌ Пожалуйста, введите ID пользователя (число) или @username",
                reply_markup=get_cancel_keyboard()
            )
            return True
        
        if opponent_id == user_id:
            await message.answer(
                "❌ Вы не можете создать дуэль с самим собой",
                reply_markup=get_cancel_keyboard()
            )
            return True
        
        # Создаем дуэль
        duel_data = await self.game_logic.create_duel(user_id, opponent_id)
        
        # Обновляем состояние
        user_states[user_id] = {
            'duel_id': duel_data['duel_id'],
            'opponent_id': opponent_id,
            'status': 'created'
        }
        
        await message.answer(
            f"⚔️ Дуэль создана! ID дуэли: {duel_data['duel_id']}\n\nОтправьте эту ссылку сопернику:\n`https://t.me/your_bot_username?start=duel_{duel_data['duel_id']}`",
            reply_markup=get_duel_share_keyboard(duel_data['duel_id']),
            parse_mode="Markdown"
        )
        
        return True
    
    async def handle_start_command(self, message: types.Message):
        """Обработка команды start"""
        from bot import cmd_start
        await cmd_start(message)
    
    async def handle_help_command(self, message: types.Message):
        """Обработка команды help"""
        from bot import cmd_help
        await cmd_help(message)
    
    async def handle_stats_command(self, message: types.Message):
        """Обработка команды stats"""
        from bot import cmd_stats
        await cmd_stats(message)
    
    async def handle_balance_command(self, message: types.Message):
        """Обработка команды balance"""
        from bot import cmd_balance
        await cmd_balance(message)
    
    async def handle_quick_choice(self, message: types.Message, choice: str, user_states: Dict[int, Dict[str, Any]]) -> bool:
        """Обработка быстрого выбора стороны монеты"""
        user_id = message.from_user.id
        
        if user_id not in user_states:
            await message.answer(
                "❌ Сначала выберите ставку и начните игру",
                reply_markup=get_main_menu_keyboard()
            )
            return True
        
        state = user_states[user_id]
        
        if 'game_id' not in state:
            await message.answer(
                "❌ Активная игра не найдена",
                reply_markup=get_main_menu_keyboard()
            )
            return True
        
        # Делаем ход
        result = await self.game_logic.make_bot_choice(state['game_id'], choice)
        
        if 'error' in result:
            await message.answer(
                "❌ Ошибка в игре. Попробуйте еще раз.",
                reply_markup=get_main_menu_keyboard()
            )
            return True
        
        # Обновляем баланс и статистику
        if result['player_won']:
            await self.db.update_balance(user_id, result['win_amount'] - result['bet'])
            await self.db.record_game_result(
                user_id, 'bot', result['bet'], choice, 'win', result['win_amount']
            )
            result_text = self.game_logic.get_win_message(result['win_amount'])
        else:
            await self.db.update_balance(user_id, -result['bet'])
            await self.db.record_game_result(
                user_id, 'bot', result['bet'], choice, 'loss', 0
            )
            result_text = self.game_logic.get_lose_message(result['bet'])
        
        # Показываем результат
        coin_side = "Орёл" if result['coin_result'] == 'heads' else "Решка"
        final_text = f"{MESSAGES['game_result']}\n\n{result_text}\n\n🪙 Выпало: {coin_side}"
        
        await message.answer(
            final_text,
            reply_markup=get_game_result_keyboard()
        )
        
        # Очищаем состояние
        if user_id in user_states:
            del user_states[user_id]
        
        return True
    
    async def handle_quick_bet(self, message: types.Message, bet: int, user_states: Dict[int, Dict[str, Any]]) -> bool:
        """Обработка быстрой ставки"""
        user_id = message.from_user.id
        
        # Проверяем баланс
        stats = await self.db.get_player_stats(user_id)
        if not stats or stats['balance'] < bet:
            await message.answer(
                MESSAGES['not_enough_balance'].format(balance=stats['balance'] if stats else 0),
                reply_markup=get_balance_keyboard()
            )
            return True
        
        # Создаем игру
        game_data = await self.game_logic.start_bot_game(user_id, bet)
        
        # Сохраняем состояние
        user_states[user_id] = {
            'game_id': game_data['game_id'],
            'bet': bet,
            'game_type': 'bot'
        }
        
        # Показываем выбор стороны монеты
        await message.answer(
            MESSAGES['choose_side'],
            reply_markup=get_coin_choice_keyboard()
        )
        
        return True