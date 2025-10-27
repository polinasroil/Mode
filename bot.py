import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, MagicData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent

from config import BOT_TOKEN, MESSAGES, MIN_BET, MAX_BET, EMOJI
from database import Database
from game_logic import GameLogic
from keyboards import *

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация бота
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Инициализация базы данных и игровой логики
db = Database()
game_logic = GameLogic()

# Состояния FSM
class GameStates(StatesGroup):
    waiting_for_bet = State()
    waiting_for_choice = State()
    waiting_for_duel_bet = State()
    waiting_for_duel_choice = State()

# Хранилище активных игр пользователей
user_states: Dict[int, Dict[str, Any]] = {}

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Обработчик команды /start"""
    # Проверяем, есть ли параметры в команде start
    if message.text.startswith("/start duel_"):
        await start_with_params(message)
        return
    
    user = message.from_user
    
    # Создаем или получаем игрока
    player = await db.get_or_create_player(
        user.id, 
        user.username, 
        user.first_name, 
        user.last_name
    )
    
    # Отправляем приветственное сообщение
    await message.answer(
        MESSAGES['welcome'],
        reply_markup=get_main_menu_keyboard()
    )

@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    """Обработчик команды /help"""
    help_text = MESSAGES['help'].format(min_bet=MIN_BET, max_bet=MAX_BET)
    await message.answer(
        help_text,
        reply_markup=get_help_keyboard(),
        parse_mode="HTML"
    )

@dp.message(Command("stats"))
async def cmd_stats(message: types.Message):
    """Обработчик команды /stats"""
    stats = await db.get_player_stats(message.from_user.id)
    
    if stats:
        stats_text = MESSAGES['stats'].format(
            wins=stats['wins'],
            losses=stats['losses'],
            win_rate=stats['win_rate']
        )
        await message.answer(
            stats_text,
            reply_markup=get_stats_keyboard()
        )
    else:
        await message.answer("❌ Статистика не найдена")

@dp.message(Command("balance"))
async def cmd_balance(message: types.Message):
    """Обработчик команды /balance"""
    stats = await db.get_player_stats(message.from_user.id)
    
    if stats:
        balance_text = MESSAGES['balance'].format(balance=stats['balance'])
        await message.answer(
            balance_text,
            reply_markup=get_balance_keyboard()
        )
    else:
        await message.answer("❌ Баланс не найден")

# Обработчики callback'ов
@dp.callback_query(MagicData.F.callback_data == "game_bot")
async def game_bot_handler(callback: types.CallbackQuery):
    """Обработчик выбора игры с ботом"""
    await callback.answer()
    
    # Проверяем баланс
    stats = await db.get_player_stats(callback.from_user.id)
    if not stats or stats['balance'] < MIN_BET:
        await callback.message.edit_text(
            MESSAGES['not_enough_balance'].format(balance=stats['balance'] if stats else 0),
            reply_markup=get_balance_keyboard()
        )
        return
    
    # Показываем клавиатуру ставок
    await callback.message.edit_text(
        MESSAGES['enter_bet'].format(min_bet=MIN_BET, max_bet=MAX_BET),
        reply_markup=get_bet_keyboard()
    )

@dp.callback_query(MagicData.F.callback_data.startswith("bet_"))
async def bet_handler(callback: types.CallbackQuery):
    """Обработчик выбора ставки"""
    await callback.answer()
    
    bet_amount = int(callback.data.split("_")[1])
    
    # Проверяем баланс
    stats = await db.get_player_stats(callback.from_user.id)
    if not stats or stats['balance'] < bet_amount:
        await callback.message.edit_text(
            MESSAGES['not_enough_balance'].format(balance=stats['balance'] if stats else 0),
            reply_markup=get_balance_keyboard()
        )
        return
    
    # Создаем игру
    game_data = await game_logic.start_bot_game(callback.from_user.id, bet_amount)
    
    # Сохраняем состояние
    user_states[callback.from_user.id] = {
        'game_id': game_data['game_id'],
        'bet': bet_amount,
        'game_type': 'bot'
    }
    
    # Показываем выбор стороны монеты
    await callback.message.edit_text(
        MESSAGES['choose_side'],
        reply_markup=get_coin_choice_keyboard()
    )

@dp.callback_query(MagicData.F.callback_data == "custom_bet")
async def custom_bet_handler(callback: types.CallbackQuery):
    """Обработчик кастомной ставки"""
    await callback.answer()
    
    # Устанавливаем состояние ожидания кастомной ставки
    user_states[callback.from_user.id] = {
        'waiting_bet': True
    }
    
    await callback.message.edit_text(
        f"💰 Введите сумму ставки (от {MIN_BET} до {MAX_BET}):\n\nПросто напишите число в чат.",
        reply_markup=get_cancel_keyboard()
    )

@dp.callback_query(MagicData.F.callback_data.startswith("choice_"))
async def choice_handler(callback: types.CallbackQuery):
    """Обработчик выбора стороны монеты"""
    await callback.answer()
    
    choice = callback.data.split("_")[1]  # heads или tails
    
    user_id = callback.from_user.id
    if user_id not in user_states:
        await callback.message.edit_text(
            "❌ Игра не найдена. Начните новую игру.",
            reply_markup=get_main_menu_keyboard()
        )
        return
    
    game_data = user_states[user_id]
    game_id = game_data['game_id']
    
    # Показываем анимацию
    animation_msg = await callback.message.edit_text(
        game_logic.get_coin_animation()
    )
    
    # Ждем немного для эффекта
    await asyncio.sleep(2)
    
    # Делаем ход
    result = await game_logic.make_bot_choice(game_id, choice)
    
    if 'error' in result:
        await callback.message.edit_text(
            "❌ Ошибка в игре. Попробуйте еще раз.",
            reply_markup=get_main_menu_keyboard()
        )
        return
    
    # Обновляем баланс и статистику
    if result['player_won']:
        await db.update_balance(user_id, result['win_amount'] - result['bet'])
        await db.record_game_result(
            user_id, 'bot', result['bet'], choice, 'win', result['win_amount']
        )
        result_text = game_logic.get_win_message(result['win_amount'])
    else:
        await db.update_balance(user_id, -result['bet'])
        await db.record_game_result(
            user_id, 'bot', result['bet'], choice, 'loss', 0
        )
        result_text = game_logic.get_lose_message(result['bet'])
    
    # Показываем результат
    coin_side = "Орёл" if result['coin_result'] == 'heads' else "Решка"
    final_text = f"{MESSAGES['game_result']}\n\n{result_text}\n\n🪙 Выпало: {coin_side}"
    
    await callback.message.edit_text(
        final_text,
        reply_markup=get_game_result_keyboard()
    )
    
    # Очищаем состояние
    if user_id in user_states:
        del user_states[user_id]

@dp.callback_query(MagicData.F.callback_data == "create_duel")
async def create_duel_handler(callback: types.CallbackQuery):
    """Обработчик создания дуэли"""
    await callback.answer()
    
    # Генерируем уникальный ID дуэли
    duel_id = game_logic.generate_duel_id()
    
    # Создаем дуэль в базе данных
    expires_at = datetime.now() + timedelta(seconds=60)
    await db.create_duel(duel_id, callback.from_user.id, None, expires_at)
    
    # Создаем дуэль в игровой логике
    await game_logic.create_duel(callback.from_user.id, None)
    
    # Сохраняем состояние
    user_states[callback.from_user.id] = {
        'duel_id': duel_id,
        'status': 'waiting_opponent'
    }
    
    # Показываем ссылку для отправки
    share_text = f"{MESSAGES['duel_created']}\n\n`https://t.me/{(await bot.me()).username}?start=duel_{duel_id}`"
    
    await callback.message.edit_text(
        share_text,
        reply_markup=get_duel_share_keyboard(duel_id),
        parse_mode="Markdown"
    )

@dp.callback_query(MagicData.F.callback_data == "stats")
async def stats_handler(callback: types.CallbackQuery):
    """Обработчик статистики"""
    await callback.answer()
    
    stats = await db.get_player_stats(callback.from_user.id)
    
    if stats:
        stats_text = MESSAGES['stats'].format(
            wins=stats['wins'],
            losses=stats['losses'],
            win_rate=stats['win_rate']
        )
        await callback.message.edit_text(
            stats_text,
            reply_markup=get_stats_keyboard()
        )
    else:
        await callback.message.edit_text(
            "❌ Статистика не найдена",
            reply_markup=get_main_menu_keyboard()
        )

@dp.callback_query(MagicData.F.callback_data == "help")
async def help_handler(callback: types.CallbackQuery):
    """Обработчик помощи"""
    await callback.answer()
    
    help_text = MESSAGES['help'].format(min_bet=MIN_BET, max_bet=MAX_BET)
    await callback.message.edit_text(
        help_text,
        reply_markup=get_help_keyboard(),
        parse_mode="HTML"
    )

@dp.callback_query(MagicData.F.callback_data == "back_to_main")
async def back_to_main_handler(callback: types.CallbackQuery):
    """Обработчик возврата в главное меню"""
    await callback.answer()
    
    # Очищаем состояние пользователя
    user_id = callback.from_user.id
    if user_id in user_states:
        del user_states[user_id]
    
    await callback.message.edit_text(
        MESSAGES['welcome'],
        reply_markup=get_main_menu_keyboard()
    )

@dp.callback_query(MagicData.F.callback_data == "cancel")
async def cancel_handler(callback: types.CallbackQuery):
    """Обработчик отмены"""
    await callback.answer()
    
    # Очищаем состояние пользователя
    user_id = callback.from_user.id
    if user_id in user_states:
        del user_states[user_id]
    
    await callback.message.edit_text(
        MESSAGES['welcome'],
        reply_markup=get_main_menu_keyboard()
    )

@dp.callback_query(MagicData.F.callback_data == "cancel_duel")
async def cancel_duel_handler(callback: types.CallbackQuery):
    """Обработчик отмены дуэли"""
    await callback.answer()
    
    # Очищаем состояние пользователя
    user_id = callback.from_user.id
    if user_id in user_states:
        del user_states[user_id]
    
    await callback.message.edit_text(
        "❌ Дуэль отменена",
        reply_markup=get_main_menu_keyboard()
    )

# Обработчик дуэлей
@dp.callback_query(MagicData.F.callback_data.startswith("accept_duel_"))
async def accept_duel_handler(callback: types.CallbackQuery):
    """Обработчик принятия дуэли"""
    await callback.answer()
    
    duel_id = callback.data.split("_")[2]
    
    # Получаем информацию о дуэли
    duel = await db.get_duel(duel_id)
    if not duel:
        await callback.message.edit_text(
            "❌ Дуэль не найдена или истекла",
            reply_markup=get_main_menu_keyboard()
        )
        return
    
    # Принимаем дуэль
    result = await game_logic.accept_duel(duel_id, callback.from_user.id)
    
    if 'error' in result:
        await callback.message.edit_text(
            f"❌ {result['error']}",
            reply_markup=get_main_menu_keyboard()
        )
        return
    
    # Сохраняем состояние
    user_states[callback.from_user.id] = {
        'duel_id': duel_id,
        'status': 'accepted'
    }
    
    # Показываем клавиатуру ставок
    await callback.message.edit_text(
        MESSAGES['duel_accepted'],
        reply_markup=get_duel_bet_keyboard(duel_id)
    )

@dp.callback_query(MagicData.F.callback_data.startswith("decline_duel_"))
async def decline_duel_handler(callback: types.CallbackQuery):
    """Обработчик отклонения дуэли"""
    await callback.answer()
    
    await callback.message.edit_text(
        MESSAGES['duel_declined'],
        reply_markup=get_main_menu_keyboard()
    )

@dp.callback_query(MagicData.F.callback_data.startswith("duel_bet_"))
async def duel_bet_handler(callback: types.CallbackQuery):
    """Обработчик ставки в дуэли"""
    await callback.answer()
    
    parts = callback.data.split("_")
    bet_amount = int(parts[2])
    duel_id = parts[3]
    
    user_id = callback.from_user.id
    
    # Проверяем баланс
    stats = await db.get_player_stats(user_id)
    if not stats or stats['balance'] < bet_amount:
        await callback.message.edit_text(
            MESSAGES['not_enough_balance'].format(balance=stats['balance'] if stats else 0),
            reply_markup=get_balance_keyboard()
        )
        return
    
    # Устанавливаем ставку
    result = await game_logic.set_duel_bet(duel_id, user_id, bet_amount)
    
    if 'error' in result:
        await callback.message.edit_text(
            f"❌ {result['error']}",
            reply_markup=get_main_menu_keyboard()
        )
        return
    
    # Обновляем состояние
    if user_id in user_states:
        user_states[user_id]['bet'] = bet_amount
    
    # Если оба игрока сделали ставки, показываем выбор стороны
    if result['status'] == 'waiting_choices':
        await callback.message.edit_text(
            MESSAGES['choose_side'],
            reply_markup=get_duel_choice_keyboard(duel_id)
        )
    else:
        await callback.message.edit_text(
            "⏳ Ожидание ставки соперника...",
            reply_markup=get_duel_waiting_keyboard()
        )

@dp.callback_query(MagicData.F.callback_data.startswith("duel_choice_"))
async def duel_choice_handler(callback: types.CallbackQuery):
    """Обработчик выбора в дуэли"""
    await callback.answer()
    
    parts = callback.data.split("_")
    choice = parts[2]  # heads или tails
    duel_id = parts[3]
    
    user_id = callback.from_user.id
    
    # Устанавливаем выбор
    result = await game_logic.set_duel_choice(duel_id, user_id, choice)
    
    if 'error' in result:
        await callback.message.edit_text(
            f"❌ {result['error']}",
            reply_markup=get_main_menu_keyboard()
        )
        return
    
    # Если оба игрока сделали выбор, завершаем дуэль
    if 'coin_result' in result:
        # Показываем анимацию
        animation_msg = await callback.message.edit_text(
            game_logic.get_coin_animation()
        )
        
        # Ждем немного для эффекта
        await asyncio.sleep(2)
        
        # Обрабатываем результат дуэли
        await process_duel_result(duel_id, result, callback.message)
    else:
        await callback.message.edit_text(
            "⏳ Ожидание выбора соперника...",
            reply_markup=get_duel_waiting_keyboard()
        )

async def process_duel_result(duel_id: str, result: Dict[str, Any], message: types.Message):
    """Обработка результата дуэли"""
    # Получаем информацию о дуэли
    duel = await db.get_duel(duel_id)
    if not duel:
        return
    
    creator_id = duel['creator_id']
    opponent_id = duel['opponent_id']
    
    # Обновляем балансы и статистику
    if result['result'] == 'creator_won':
        # Создатель выиграл
        await db.update_balance(creator_id, result['winner_bet'] + result['loser_bet'])
        await db.update_balance(opponent_id, -result['loser_bet'])
        
        await db.record_game_result(creator_id, 'duel', result['creator_bet'], result['creator_choice'], 'win', result['winner_bet'] + result['loser_bet'])
        await db.record_game_result(opponent_id, 'duel', result['opponent_bet'], result['opponent_choice'], 'loss', 0)
        
        winner_name = "Создатель дуэли"
        loser_name = "Соперник"
        
    elif result['result'] == 'opponent_won':
        # Соперник выиграл
        await db.update_balance(opponent_id, result['winner_bet'] + result['loser_bet'])
        await db.update_balance(creator_id, -result['loser_bet'])
        
        await db.record_game_result(opponent_id, 'duel', result['opponent_bet'], result['opponent_choice'], 'win', result['winner_bet'] + result['loser_bet'])
        await db.record_game_result(creator_id, 'duel', result['creator_bet'], result['creator_choice'], 'loss', 0)
        
        winner_name = "Соперник"
        loser_name = "Создатель дуэли"
        
    else:
        # Ничья
        winner_name = "Ничья"
        loser_name = "Ничья"
    
    # Завершаем дуэль в базе данных
    await db.complete_duel(duel_id, result['result'], result['winner_id'])
    
    # Формируем текст результата
    coin_side = "Орёл" if result['coin_result'] == 'heads' else "Решка"
    
    if result['result'] == 'draw':
        result_text = f"🤝 Ничья!\n\n🪙 Выпало: {coin_side}\n\nОба игрока угадали или не угадали!"
    else:
        result_text = f"🏆 Победитель: {winner_name}!\n\n🪙 Выпало: {coin_side}\n\nВыигрыш: {result['winner_bet'] + result['loser_bet']}"
    
    # Показываем результат
    await message.edit_text(
        result_text,
        reply_markup=get_duel_result_keyboard()
    )
    
    # Очищаем состояния игроков
    if creator_id in user_states:
        del user_states[creator_id]
    if opponent_id in user_states:
        del user_states[opponent_id]

# Обработчик inline запросов
@dp.inline_query()
async def inline_query_handler(query: InlineQuery):
    """Обработчик inline запросов для дуэлей"""
    if query.query.startswith("duel_"):
        duel_id = query.query.split("_")[1]
        
        # Создаем inline результат
        result = InlineQueryResultArticle(
            id="1",
            title="🎮 Присоединиться к дуэли",
            description="Нажмите, чтобы принять вызов!",
            input_message_content=InputTextMessageContent(
                message_text=f"⚔️ Вас пригласили на дуэль!\n\nНажмите кнопку ниже, чтобы принять вызов:",
                parse_mode="HTML"
            ),
            reply_markup=get_duel_invitation_keyboard(duel_id)
        )
        
        await query.answer([result])

# Обработчик команды start с параметрами (для дуэлей)
async def start_with_params(message: types.Message):
    """Обработчик команды start с параметрами"""
    if message.text.startswith("/start duel_"):
        duel_id = message.text.split("duel_")[1]
        
        # Получаем информацию о дуэли
        duel = await db.get_duel(duel_id)
        if not duel:
            await message.answer(
                "❌ Дуэль не найдена или истекла",
                reply_markup=get_main_menu_keyboard()
            )
            return
        
        # Проверяем, не является ли пользователь создателем дуэли
        if duel['creator_id'] == message.from_user.id:
            await message.answer(
                "❌ Вы не можете принять свою же дуэль",
                reply_markup=get_main_menu_keyboard()
            )
            return
        
        # Показываем приглашение на дуэль
        await message.answer(
            f"⚔️ Вас пригласили на дуэль!\n\nНажмите кнопку ниже, чтобы принять вызов:",
            reply_markup=get_duel_invitation_keyboard(duel_id)
        )
    else:
        # Обычный start
        await cmd_start(message)

# Обработчик текстовых сообщений
@dp.message()
async def handle_text_messages(message: types.Message):
    """Обработчик всех текстовых сообщений"""
    from handlers import TextHandlers
    
    # Создаем обработчик текстовых сообщений
    text_handler = TextHandlers(db, game_logic)
    
    # Обрабатываем сообщение
    handled = await text_handler.handle_text_message(message, user_states)
    
    # Если сообщение не было обработано, показываем главное меню
    if not handled:
        await message.answer(
            "🎮 Отправьте /start для начала игры или выберите действие:",
            reply_markup=get_main_menu_keyboard()
        )

# Функция очистки истекших игр и дуэлей
async def cleanup_expired():
    """Очистка истекших игр и дуэлей"""
    while True:
        try:
            # Очищаем истекшие игры
            expired_games = await game_logic.cleanup_expired_games()
            if expired_games > 0:
                logger.info(f"Очищено {expired_games} истекших игр")
            
            # Очищаем истекшие дуэли
            expired_duels = await game_logic.cleanup_expired_duels()
            if expired_duels > 0:
                logger.info(f"Очищено {expired_duels} истекших дуэлей")
            
            # Очищаем истекшие дуэли в базе данных
            db_expired = await db.cleanup_expired_duels()
            if db_expired > 0:
                logger.info(f"Очищено {db_expired} истекших дуэлей в БД")
            
        except Exception as e:
            logger.error(f"Ошибка при очистке: {e}")
        
        # Ждем 5 минут перед следующей очисткой
        await asyncio.sleep(300)

# Запуск бота
async def main():
    """Главная функция"""
    logger.info("Запуск бота...")
    
    # Запускаем задачу очистки
    asyncio.create_task(cleanup_expired())
    
    # Запускаем бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())