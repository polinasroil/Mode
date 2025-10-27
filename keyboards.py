from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import EMOJI

def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Главное меню"""
    builder = InlineKeyboardBuilder()
    
    builder.add(InlineKeyboardButton(
        text=f"{EMOJI['game']} Игра с ботом",
        callback_data="game_bot"
    ))
    builder.add(InlineKeyboardButton(
        text=f"{EMOJI['sword']} Создать дуэль",
        callback_data="create_duel"
    ))
    builder.add(InlineKeyboardButton(
        text=f"{EMOJI['stats']} Статистика",
        callback_data="stats"
    ))
    builder.add(InlineKeyboardButton(
        text=f"{EMOJI['help']} Помощь",
        callback_data="help"
    ))
    
    builder.adjust(2)
    return builder.as_markup()

def get_coin_choice_keyboard() -> InlineKeyboardMarkup:
    """Выбор стороны монеты"""
    builder = InlineKeyboardBuilder()
    
    builder.add(InlineKeyboardButton(
        text=f"{EMOJI['heads']} Орёл",
        callback_data="choice_heads"
    ))
    builder.add(InlineKeyboardButton(
        text=f"{EMOJI['tails']} Решка",
        callback_data="choice_tails"
    ))
    builder.add(InlineKeyboardButton(
        text=f"{EMOJI['back']} Назад",
        callback_data="back_to_main"
    ))
    
    builder.adjust(2, 1)
    return builder.as_markup()

def get_duel_invitation_keyboard(duel_id: str) -> InlineKeyboardMarkup:
    """Клавиатура приглашения на дуэль"""
    builder = InlineKeyboardBuilder()
    
    builder.add(InlineKeyboardButton(
        text=f"{EMOJI['check']} Принять дуэль",
        callback_data=f"accept_duel_{duel_id}"
    ))
    builder.add(InlineKeyboardButton(
        text=f"{EMOJI['cross']} Отклонить",
        callback_data=f"decline_duel_{duel_id}"
    ))
    
    builder.adjust(2)
    return builder.as_markup()

def get_duel_share_keyboard(duel_id: str) -> InlineKeyboardMarkup:
    """Клавиатура для отправки дуэли"""
    builder = InlineKeyboardBuilder()
    
    builder.add(InlineKeyboardButton(
        text=f"{EMOJI['sword']} Отправить дуэль",
        switch_inline_query=f"duel_{duel_id}"
    ))
    builder.add(InlineKeyboardButton(
        text=f"{EMOJI['back']} Назад",
        callback_data="back_to_main"
    ))
    
    builder.adjust(1)
    return builder.as_markup()

def get_bet_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура быстрых ставок"""
    builder = InlineKeyboardBuilder()
    
    builder.add(InlineKeyboardButton(
        text="10",
        callback_data="bet_10"
    ))
    builder.add(InlineKeyboardButton(
        text="25",
        callback_data="bet_25"
    ))
    builder.add(InlineKeyboardButton(
        text="50",
        callback_data="bet_50"
    ))
    builder.add(InlineKeyboardButton(
        text="100",
        callback_data="bet_100"
    ))
    builder.add(InlineKeyboardButton(
        text="250",
        callback_data="bet_250"
    ))
    builder.add(InlineKeyboardButton(
        text="500",
        callback_data="bet_500"
    ))
    builder.add(InlineKeyboardButton(
        text="1000",
        callback_data="bet_1000"
    ))
    builder.add(InlineKeyboardButton(
        text="💰 Своя ставка",
        callback_data="custom_bet"
    ))
    builder.add(InlineKeyboardButton(
        text=f"{EMOJI['back']} Назад",
        callback_data="back_to_main"
    ))
    
    builder.adjust(3, 3, 1, 1, 1)
    return builder.as_markup()

def get_game_result_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура после результата игры"""
    builder = InlineKeyboardBuilder()
    
    builder.add(InlineKeyboardButton(
        text=f"{EMOJI['game']} Играть еще",
        callback_data="game_bot"
    ))
    builder.add(InlineKeyboardButton(
        text=f"{EMOJI['sword']} Создать дуэль",
        callback_data="create_duel"
    ))
    builder.add(InlineKeyboardButton(
        text=f"{EMOJI['back']} Главное меню",
        callback_data="back_to_main"
    ))
    
    builder.adjust(2, 1)
    return builder.as_markup()

def get_duel_result_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура после результата дуэли"""
    builder = InlineKeyboardBuilder()
    
    builder.add(InlineKeyboardButton(
        text=f"{EMOJI['sword']} Новая дуэль",
        callback_data="create_duel"
    ))
    builder.add(InlineKeyboardButton(
        text=f"{EMOJI['game']} Игра с ботом",
        callback_data="game_bot"
    ))
    builder.add(InlineKeyboardButton(
        text=f"{EMOJI['back']} Главное меню",
        callback_data="back_to_main"
    ))
    
    builder.adjust(2, 1)
    return builder.as_markup()

def get_stats_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура статистики"""
    builder = InlineKeyboardBuilder()
    
    builder.add(InlineKeyboardButton(
        text=f"{EMOJI['game']} Играть",
        callback_data="game_bot"
    ))
    builder.add(InlineKeyboardButton(
        text=f"{EMOJI['back']} Назад",
        callback_data="back_to_main"
    ))
    
    builder.adjust(2)
    return builder.as_markup()

def get_help_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура помощи"""
    builder = InlineKeyboardBuilder()
    
    builder.add(InlineKeyboardButton(
        text=f"{EMOJI['game']} Начать игру",
        callback_data="game_bot"
    ))
    builder.add(InlineKeyboardButton(
        text=f"{EMOJI['back']} Назад",
        callback_data="back_to_main"
    ))
    
    builder.adjust(2)
    return builder.as_markup()

def get_cancel_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура отмены"""
    builder = InlineKeyboardBuilder()
    
    builder.add(InlineKeyboardButton(
        text=f"{EMOJI['cross']} Отменить",
        callback_data="cancel"
    ))
    
    return builder.as_markup()

def get_duel_waiting_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура ожидания дуэли"""
    builder = InlineKeyboardBuilder()
    
    builder.add(InlineKeyboardButton(
        text=f"{EMOJI['cross']} Отменить дуэль",
        callback_data="cancel_duel"
    ))
    
    return builder.as_markup()

def get_duel_choice_keyboard(duel_id: str) -> InlineKeyboardMarkup:
    """Клавиатура выбора в дуэли"""
    builder = InlineKeyboardBuilder()
    
    builder.add(InlineKeyboardButton(
        text=f"{EMOJI['heads']} Орёл",
        callback_data=f"duel_choice_heads_{duel_id}"
    ))
    builder.add(InlineKeyboardButton(
        text=f"{EMOJI['tails']} Решка",
        callback_data=f"duel_choice_tails_{duel_id}"
    ))
    
    builder.adjust(2)
    return builder.as_markup()

def get_duel_bet_keyboard(duel_id: str) -> InlineKeyboardMarkup:
    """Клавиатура ставок в дуэли"""
    builder = InlineKeyboardBuilder()
    
    builder.add(InlineKeyboardButton(
        text="10",
        callback_data=f"duel_bet_10_{duel_id}"
    ))
    builder.add(InlineKeyboardButton(
        text="25",
        callback_data=f"duel_bet_25_{duel_id}"
    ))
    builder.add(InlineKeyboardButton(
        text="50",
        callback_data=f"duel_bet_50_{duel_id}"
    ))
    builder.add(InlineKeyboardButton(
        text="100",
        callback_data=f"duel_bet_100_{duel_id}"
    ))
    builder.add(InlineKeyboardButton(
        text="250",
        callback_data=f"duel_bet_250_{duel_id}"
    ))
    builder.add(InlineKeyboardButton(
        text="500",
        callback_data=f"duel_bet_500_{duel_id}"
    ))
    builder.add(InlineKeyboardButton(
        text="1000",
        callback_data=f"duel_bet_1000_{duel_id}"
    ))
    builder.add(InlineKeyboardButton(
        text=f"{EMOJI['cross']} Отменить",
        callback_data="cancel_duel"
    ))
    
    builder.adjust(3, 3, 1, 1)
    return builder.as_markup()

def get_balance_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура баланса"""
    builder = InlineKeyboardBuilder()
    
    builder.add(InlineKeyboardButton(
        text=f"{EMOJI['game']} Играть",
        callback_data="game_bot"
    ))
    builder.add(InlineKeyboardButton(
        text=f"{EMOJI['back']} Назад",
        callback_data="back_to_main"
    ))
    
    builder.adjust(2)
    return builder.as_markup()