#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Подробная система логирования для Minecraft PE Server
"""

import logging
import os
import time
from datetime import datetime

class DetailedLogger:
    """Подробный логгер для отладки"""
    
    def __init__(self, log_dir="logs"):
        self.log_dir = log_dir
        self.setup_logging()
    
    def setup_logging(self):
        """Настройка логирования"""
        # Создаем директорию для логов
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Основной логгер
        self.logger = logging.getLogger('minecraft_detailed')
        self.logger.setLevel(logging.DEBUG)
        
        # Очищаем существующие обработчики
        self.logger.handlers.clear()
        
        # Файловый обработчик для подробных логов
        detailed_handler = logging.FileHandler(
            os.path.join(self.log_dir, f'detailed_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
            encoding='utf-8'
        )
        detailed_handler.setLevel(logging.DEBUG)
        
        # Форматтер для подробных логов
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        detailed_handler.setFormatter(detailed_formatter)
        
        # Консольный обработчик
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Форматтер для консоли
        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        
        # Добавляем обработчики
        self.logger.addHandler(detailed_handler)
        self.logger.addHandler(console_handler)
        
        # Логгер для протокола
        self.protocol_logger = logging.getLogger('minecraft_protocol')
        self.protocol_logger.setLevel(logging.DEBUG)
        
        # Файловый обработчик для протокола
        protocol_handler = logging.FileHandler(
            os.path.join(self.log_dir, f'protocol_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
            encoding='utf-8'
        )
        protocol_handler.setLevel(logging.DEBUG)
        protocol_handler.setFormatter(detailed_formatter)
        self.protocol_logger.addHandler(protocol_handler)
        
        # Логгер для мира
        self.world_logger = logging.getLogger('minecraft_world')
        self.world_logger.setLevel(logging.DEBUG)
        
        # Файловый обработчик для мира
        world_handler = logging.FileHandler(
            os.path.join(self.log_dir, f'world_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
            encoding='utf-8'
        )
        world_handler.setLevel(logging.DEBUG)
        world_handler.setFormatter(detailed_formatter)
        self.world_logger.addHandler(world_handler)
    
    def log_connection_attempt(self, addr, data_length):
        """Логирование попытки подключения"""
        self.protocol_logger.info(f"🔌 ПОПЫТКА ПОДКЛЮЧЕНИЯ: {addr}, данные: {data_length} байт")
    
    def log_packet_received(self, packet_id, addr, data_length):
        """Логирование полученного пакета"""
        self.protocol_logger.debug(f"📥 ПАКЕТ ПОЛУЧЕН: ID={packet_id:02X}, от {addr}, размер: {data_length} байт")
    
    def log_packet_sent(self, packet_id, addr, data_length):
        """Логирование отправленного пакета"""
        self.protocol_logger.debug(f"📤 ПАКЕТ ОТПРАВЛЕН: ID={packet_id:02X}, на {addr}, размер: {data_length} байт")
    
    def log_player_login_start(self, username, addr, entity_id):
        """Логирование начала входа игрока"""
        self.logger.info(f"🚀 НАЧАЛО ВХОДА ИГРОКА: {username} с {addr}, Entity ID: {entity_id}")
    
    def log_player_login_step(self, username, step, details=""):
        """Логирование шага входа игрока"""
        self.logger.info(f"📋 ШАГ ВХОДА {username}: {step} {details}")
    
    def log_player_login_complete(self, username):
        """Логирование завершения входа игрока"""
        self.logger.info(f"✅ ВХОД ИГРОКА ЗАВЕРШЕН: {username}")
    
    def log_world_generation(self, chunk_x, chunk_z, block_count):
        """Логирование генерации мира"""
        self.world_logger.info(f"🌍 ГЕНЕРАЦИЯ ЧАНКА: ({chunk_x}, {chunk_z}), блоков: {block_count}")
    
    def log_chunk_sent(self, username, chunk_x, chunk_z, data_size):
        """Логирование отправки чанка"""
        self.world_logger.info(f"📦 ЧАНК ОТПРАВЛЕН: {username} -> ({chunk_x}, {chunk_z}), размер: {data_size} байт")
    
    def log_error(self, error_type, details, traceback_info=""):
        """Логирование ошибок"""
        self.logger.error(f"❌ ОШИБКА {error_type}: {details}")
        if traceback_info:
            self.logger.error(f"📚 TRACEBACK: {traceback_info}")
    
    def log_debug_info(self, info_type, details):
        """Логирование отладочной информации"""
        self.logger.debug(f"🔍 DEBUG {info_type}: {details}")

# Глобальный экземпляр логгера
detailed_logger = DetailedLogger()