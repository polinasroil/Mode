#!/usr/bin/env python3
"""
Тесты для Telegram бота "Орёл или решка"

Этот файл содержит unit-тесты для проверки основных функций бота.
"""

import unittest
import asyncio
import tempfile
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch

# Импортируем модули для тестирования
from game_logic import GameLogic
from database import Database
from utils import (
    validate_bet, validate_choice, format_balance, 
    calculate_win_rate, get_coin_side_name, is_expired
)

class TestGameLogic(unittest.TestCase):
    """Тесты игровой логики"""
    
    def setUp(self):
        """Настройка перед каждым тестом"""
        self.game_logic = GameLogic()
    
    def test_flip_coin(self):
        """Тест подбрасывания монеты"""
        result = self.game_logic.flip_coin()
        self.assertIn(result, ['heads', 'tails'])
    
    def test_check_win(self):
        """Тест проверки выигрыша"""
        # Правильный выбор
        self.assertTrue(self.game_logic.check_win('heads', 'heads'))
        self.assertTrue(self.game_logic.check_win('tails', 'tails'))
        
        # Неправильный выбор
        self.assertFalse(self.game_logic.check_win('heads', 'tails'))
        self.assertFalse(self.game_logic.check_win('tails', 'heads'))
    
    def test_calculate_win_amount(self):
        """Тест расчета выигрыша"""
        self.assertEqual(self.game_logic.calculate_win_amount(10), 20)
        self.assertEqual(self.game_logic.calculate_win_amount(100), 200)
        self.assertEqual(self.game_logic.calculate_win_amount(0), 0)
    
    def test_generate_duel_id(self):
        """Тест генерации ID дуэли"""
        duel_id1 = self.game_logic.generate_duel_id()
        duel_id2 = self.game_logic.generate_duel_id()
        
        self.assertIsInstance(duel_id1, str)
        self.assertIsInstance(duel_id2, str)
        self.assertNotEqual(duel_id1, duel_id2)
        self.assertEqual(len(duel_id1), 8)
        self.assertEqual(len(duel_id2), 8)

class TestDatabase(unittest.TestCase):
    """Тесты базы данных"""
    
    def setUp(self):
        """Настройка перед каждым тестом"""
        # Создаем временную базу данных
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db = Database(self.temp_db.name)
    
    def tearDown(self):
        """Очистка после каждого теста"""
        # Удаляем временную базу данных
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    async def test_get_or_create_player(self):
        """Тест получения/создания игрока"""
        # Создаем нового игрока
        player = await self.db.get_or_create_player(
            user_id=12345,
            username="test_user",
            first_name="Test",
            last_name="User"
        )
        
        self.assertEqual(player['user_id'], 12345)
        self.assertEqual(player['username'], "test_user")
        self.assertEqual(player['balance'], 1000)
        self.assertEqual(player['wins'], 0)
        self.assertEqual(player['losses'], 0)
        
        # Получаем существующего игрока
        player2 = await self.db.get_or_create_player(
            user_id=12345,
            username="test_user2"
        )
        
        self.assertEqual(player2['user_id'], 12345)
        self.assertEqual(player2['username'], "test_user")  # Не изменился
        self.assertEqual(player2['balance'], 1000)
    
    async def test_update_balance(self):
        """Тест обновления баланса"""
        # Создаем игрока
        await self.db.get_or_create_player(user_id=12345)
        
        # Увеличиваем баланс
        success = await self.db.update_balance(12345, 500)
        self.assertTrue(success)
        
        # Проверяем новый баланс
        player = await self.db.get_or_create_player(user_id=12345)
        self.assertEqual(player['balance'], 1500)
        
        # Уменьшаем баланс
        success = await self.db.update_balance(12345, -200)
        self.assertTrue(success)
        
        player = await self.db.get_or_create_player(user_id=12345)
        self.assertEqual(player['balance'], 1300)
    
    async def test_record_game_result(self):
        """Тест записи результата игры"""
        # Создаем игрока
        await self.db.get_or_create_player(user_id=12345)
        
        # Записываем победу
        success = await self.db.record_game_result(
            user_id=12345,
            game_type='bot',
            bet=100,
            choice='heads',
            result='win',
            win_amount=200
        )
        self.assertTrue(success)
        
        # Проверяем статистику
        stats = await self.db.get_player_stats(12345)
        self.assertEqual(stats['wins'], 1)
        self.assertEqual(stats['losses'], 0)
        self.assertEqual(stats['total_games'], 1)
        
        # Записываем поражение
        success = await self.db.record_game_result(
            user_id=12345,
            game_type='bot',
            bet=50,
            choice='tails',
            result='loss',
            win_amount=0
        )
        self.assertTrue(success)
        
        # Проверяем обновленную статистику
        stats = await self.db.get_player_stats(12345)
        self.assertEqual(stats['wins'], 1)
        self.assertEqual(stats['losses'], 1)
        self.assertEqual(stats['total_games'], 2)

class TestUtils(unittest.TestCase):
    """Тесты утилит"""
    
    def test_validate_bet(self):
        """Тест валидации ставки"""
        # Валидные ставки
        self.assertEqual(validate_bet("10"), 10)
        self.assertEqual(validate_bet("100"), 100)
        self.assertEqual(validate_bet("1000"), 1000)
        
        # Невалидные ставки
        self.assertIsNone(validate_bet("0"))
        self.assertIsNone(validate_bet("1001"))
        self.assertIsNone(validate_bet("abc"))
        self.assertIsNone(validate_bet(""))
        self.assertIsNone(validate_bet("-10"))
    
    def test_validate_choice(self):
        """Тест валидации выбора"""
        # Валидные выборы (русские)
        self.assertEqual(validate_choice("орёл"), "heads")
        self.assertEqual(validate_choice("орел"), "heads")
        self.assertEqual(validate_choice("решка"), "tails")
        
        # Валидные выборы (английские)
        self.assertEqual(validate_choice("heads"), "heads")
        self.assertEqual(validate_choice("tails"), "tails")
        
        # Невалидные выборы
        self.assertIsNone(validate_choice("монета"))
        self.assertIsNone(validate_choice(""))
        self.assertIsNone(validate_choice("123"))
    
    def test_format_balance(self):
        """Тест форматирования баланса"""
        self.assertEqual(format_balance(100), "100")
        self.assertEqual(format_balance(1500), "1.5K")
        self.assertEqual(format_balance(1000000), "1.0M")
        self.assertEqual(format_balance(2500000), "2.5M")
    
    def test_calculate_win_rate(self):
        """Тест расчета процента побед"""
        self.assertEqual(calculate_win_rate(0, 0), 0.0)
        self.assertEqual(calculate_win_rate(5, 5), 50.0)
        self.assertEqual(calculate_win_rate(10, 0), 100.0)
        self.assertEqual(calculate_win_rate(0, 10), 0.0)
        self.assertEqual(calculate_win_rate(3, 7), 30.0)
    
    def test_get_coin_side_name(self):
        """Тест получения названия стороны монеты"""
        self.assertEqual(get_coin_side_name("heads"), "Орёл")
        self.assertEqual(get_coin_side_name("tails"), "Решка")
    
    def test_is_expired(self):
        """Тест проверки истечения времени"""
        now = datetime.now()
        
        # Не истекло
        future = now + timedelta(seconds=60)
        self.assertFalse(is_expired(future, 30))
        
        # Истекло
        past = now - timedelta(seconds=60)
        self.assertTrue(is_expired(past, 30))

class TestIntegration(unittest.TestCase):
    """Интеграционные тесты"""
    
    def setUp(self):
        """Настройка перед каждым тестом"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db = Database(self.temp_db.name)
        self.game_logic = GameLogic()
    
    def tearDown(self):
        """Очистка после каждого теста"""
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    async def test_complete_game_flow(self):
        """Тест полного цикла игры"""
        # Создаем игрока
        player = await self.db.get_or_create_player(user_id=12345)
        initial_balance = player['balance']
        
        # Создаем игру
        game_data = await self.game_logic.start_bot_game(12345, 100)
        
        # Делаем выбор
        result = await self.game_logic.make_bot_choice(game_data['game_id'], 'heads')
        
        # Обновляем баланс и статистику
        if result['player_won']:
            await self.db.update_balance(12345, result['win_amount'] - result['bet'])
            await self.db.record_game_result(
                12345, 'bot', result['bet'], 'heads', 'win', result['win_amount']
            )
        else:
            await self.db.update_balance(12345, -result['bet'])
            await self.db.record_game_result(
                12345, 'bot', result['bet'], 'heads', 'loss', 0
            )
        
        # Проверяем результат
        final_player = await self.db.get_or_create_player(user_id=12345)
        stats = await self.db.get_player_stats(12345)
        
        self.assertIsNotNone(stats)
        self.assertEqual(stats['total_games'], 1)
        
        if result['player_won']:
            self.assertEqual(stats['wins'], 1)
            self.assertEqual(stats['losses'], 0)
            self.assertEqual(final_player['balance'], initial_balance + 100)
        else:
            self.assertEqual(stats['wins'], 0)
            self.assertEqual(stats['losses'], 1)
            self.assertEqual(final_player['balance'], initial_balance - 100)

def run_tests():
    """Запуск всех тестов"""
    print("🧪 Запуск тестов для Telegram бота 'Орёл или решка'...")
    print("=" * 60)
    
    # Создаем test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Добавляем тесты
    suite.addTests(loader.loadTestsFromTestCase(TestGameLogic))
    suite.addTests(loader.loadTestsFromTestCase(TestDatabase))
    suite.addTests(loader.loadTestsFromTestCase(TestUtils))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Запускаем тесты
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Выводим результат
    print("=" * 60)
    if result.wasSuccessful():
        print("✅ Все тесты прошли успешно!")
    else:
        print(f"❌ Тесты завершились с ошибками: {len(result.failures)} failures, {len(result.errors)} errors")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    # Запускаем тесты
    success = run_tests()
    
    # Возвращаем код выхода
    exit(0 if success else 1)