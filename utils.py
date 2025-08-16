"""
Утилиты для Telegram бота "Орёл или решка"
"""

import re
import asyncio
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

def validate_bet(bet_str: str, min_bet: int = 1, max_bet: int = 1000) -> Optional[int]:
    """
    Валидация ставки
    
    Args:
        bet_str: Строка со ставкой
        min_bet: Минимальная ставка
        max_bet: Максимальная ставка
    
    Returns:
        int: Валидная ставка или None
    """
    try:
        bet = int(bet_str.strip())
        if min_bet <= bet <= max_bet:
            return bet
    except ValueError:
        pass
    return None

def validate_choice(choice_str: str) -> Optional[str]:
    """
    Валидация выбора стороны монеты
    
    Args:
        choice_str: Строка с выбором
    
    Returns:
        str: 'heads' или 'tails' или None
    """
    choice = choice_str.strip().lower()
    
    # Русские варианты
    if choice in ['орёл', 'орел', 'орла', 'орлом']:
        return 'heads'
    elif choice in ['решка', 'решку', 'решкой']:
        return 'tails'
    
    # Английские варианты
    elif choice in ['heads', 'head']:
        return 'heads'
    elif choice in ['tails', 'tail']:
        return 'tails'
    
    return None

def format_balance(balance: int) -> str:
    """
    Форматирование баланса для отображения
    
    Args:
        balance: Баланс в числах
    
    Returns:
        str: Отформатированный баланс
    """
    if balance >= 1000000:
        return f"{balance / 1000000:.1f}M"
    elif balance >= 1000:
        return f"{balance / 1000:.1f}K"
    else:
        return str(balance)

def format_time_duration(seconds: int) -> str:
    """
    Форматирование длительности времени
    
    Args:
        seconds: Количество секунд
    
    Returns:
        str: Отформатированное время
    """
    if seconds < 60:
        return f"{seconds}с"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes}м {seconds % 60}с"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}ч {minutes}м"

def calculate_win_rate(wins: int, losses: int) -> float:
    """
    Расчет процента побед
    
    Args:
        wins: Количество побед
        losses: Количество поражений
    
    Returns:
        float: Процент побед
    """
    total = wins + losses
    if total == 0:
        return 0.0
    return round((wins / total) * 100, 1)

def get_coin_side_name(choice: str) -> str:
    """
    Получение названия стороны монеты
    
    Args:
        choice: 'heads' или 'tails'
    
    Returns:
        str: Название стороны
    """
    return "Орёл" if choice == 'heads' else "Решка"

def get_game_type_name(game_type: str) -> str:
    """
    Получение названия типа игры
    
    Args:
        game_type: Тип игры
    
    Returns:
        str: Название типа игры
    """
    types = {
        'bot': 'Игра с ботом',
        'duel': 'Дуэль',
        'tournament': 'Турнир'
    }
    return types.get(game_type, game_type)

def sanitize_username(username: str) -> str:
    """
    Очистка username от специальных символов
    
    Args:
        username: Исходный username
    
    Returns:
        str: Очищенный username
    """
    # Убираем @ в начале
    if username.startswith('@'):
        username = username[1:]
    
    # Убираем специальные символы
    username = re.sub(r'[^\w]', '', username)
    
    return username

def is_valid_user_id(user_id_str: str) -> bool:
    """
    Проверка валидности ID пользователя
    
    Args:
        user_id_str: Строка с ID пользователя
    
    Returns:
        bool: True если валидный ID
    """
    try:
        user_id = int(user_id_str)
        return user_id > 0
    except ValueError:
        return False

def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Обрезка текста до максимальной длины
    
    Args:
        text: Исходный текст
        max_length: Максимальная длина
    
    Returns:
        str: Обрезанный текст
    """
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def format_game_history(game_data: Dict[str, Any]) -> str:
    """
    Форматирование истории игры для отображения
    
    Args:
        game_data: Данные игры
    
    Returns:
        str: Отформатированная история
    """
    game_type = get_game_type_name(game_data.get('game_type', 'unknown'))
    bet = game_data.get('bet', 0)
    choice = get_coin_side_name(game_data.get('choice', 'unknown'))
    result = game_data.get('result', 'unknown')
    win_amount = game_data.get('win_amount', 0)
    created_at = game_data.get('created_at', datetime.now())
    
    if isinstance(created_at, str):
        created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
    
    date_str = created_at.strftime("%d.%m.%Y %H:%M")
    
    if result == 'win':
        result_emoji = "✅"
        result_text = f"Выигрыш: +{win_amount}"
    else:
        result_emoji = "❌"
        result_text = f"Проигрыш: -{bet}"
    
    return f"{result_emoji} {date_str} | {game_type} | Ставка: {bet} | {choice} | {result_text}"

async def delay_with_progress(seconds: int, progress_callback=None) -> None:
    """
    Задержка с возможностью отображения прогресса
    
    Args:
        seconds: Количество секунд задержки
        progress_callback: Функция для отображения прогресса
    """
    for i in range(seconds):
        if progress_callback:
            await progress_callback(i + 1, seconds)
        await asyncio.sleep(1)

def generate_invite_link(bot_username: str, duel_id: str) -> str:
    """
    Генерация ссылки-приглашения для дуэли
    
    Args:
        bot_username: Username бота
        duel_id: ID дуэли
    
    Returns:
        str: Ссылка-приглашение
    """
    return f"https://t.me/{bot_username}?start=duel_{duel_id}"

def parse_duel_id_from_start_param(start_param: str) -> Optional[str]:
    """
    Извлечение ID дуэли из параметра start
    
    Args:
        start_param: Параметр start
    
    Returns:
        str: ID дуэли или None
    """
    if start_param.startswith('duel_'):
        return start_param[5:]  # Убираем 'duel_'
    return None

def is_expired(timestamp: datetime, timeout_seconds: int) -> bool:
    """
    Проверка истечения времени
    
    Args:
        timestamp: Временная метка
        timeout_seconds: Таймаут в секундах
    
    Returns:
        bool: True если истекло
    """
    if isinstance(timestamp, str):
        timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    
    return datetime.now() > timestamp + timedelta(seconds=timeout_seconds)