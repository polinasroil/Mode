#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Minecraft PE Server - Система сжатия данных
Автор: Minecraft PE Server Team
Версия: 1.0.0
Основано на официальной спецификации сжатия Minecraft Bedrock
"""

import zlib
import logging
import struct
from typing import Optional, Tuple
from enum import Enum

logger = logging.getLogger(__name__)

class CompressionType(Enum):
    """Типы сжатия"""
    NONE = 0
    ZLIB = 1
    SNAPPY = 2
    LZ4 = 3

class CompressionManager:
    """Менеджер сжатия данных для Minecraft Bedrock"""
    
    def __init__(self, compression_type: CompressionType = CompressionType.ZLIB, level: int = 6):
        self.compression_type = compression_type
        self.compression_level = level
        self.compressor = None
        self.decompressor = None
        
        # Инициализация компрессоров
        if compression_type == CompressionType.ZLIB:
            self.compressor = zlib.compressobj(level)
            self.decompressor = zlib.decompressobj()
        
        logger.info(f"Система сжатия инициализирована: {compression_type.name} (уровень: {level})")
    
    def compress_data(self, data: bytes, threshold: int = 1024) -> Tuple[bytes, bool]:
        """
        Сжатие данных
        
        Args:
            data: Данные для сжатия
            threshold: Минимальный размер для сжатия
            
        Returns:
            Tuple[bytes, bool]: (сжатые данные, был ли применен компрессор)
        """
        try:
            if len(data) < threshold:
                # Данные слишком малы для сжатия
                return data, False
            
            if self.compression_type == CompressionType.NONE:
                return data, False
            
            elif self.compression_type == CompressionType.ZLIB:
                if self.compressor:
                    compressed = self.compressor.compress(data)
                    compressed += self.compressor.flush()
                    
                    # Проверяем, выгодно ли сжатие
                    if len(compressed) < len(data):
                        return compressed, True
                    else:
                        return data, False
                else:
                    return data, False
            
            elif self.compression_type == CompressionType.SNAPPY:
                # Snappy сжатие (если доступно)
                try:
                    import snappy
                    compressed = snappy.compress(data)
                    if len(compressed) < len(data):
                        return compressed, True
                    else:
                        return data, False
                except ImportError:
                    logger.warning("Snappy не доступен, используем ZLIB")
                    return self.compress_data(data, threshold)
            
            elif self.compression_type == CompressionType.LZ4:
                # LZ4 сжатие (если доступно)
                try:
                    import lz4.frame
                    compressed = lz4.frame.compress(data, compression_level=self.compression_level)
                    if len(compressed) < len(data):
                        return compressed, True
                    else:
                        return data, False
                except ImportError:
                    logger.warning("LZ4 не доступен, используем ZLIB")
                    return self.compress_data(data, threshold)
            
            return data, False
            
        except Exception as e:
            logger.error(f"Ошибка сжатия данных: {e}")
            return data, False
    
    def decompress_data(self, data: bytes, was_compressed: bool) -> bytes:
        """
        Распаковка данных
        
        Args:
            data: Данные для распаковки
            was_compressed: Были ли данные сжаты
            
        Returns:
            bytes: Распакованные данные
        """
        try:
            if not was_compressed:
                return data
            
            if self.compression_type == CompressionType.NONE:
                return data
            
            elif self.compression_type == CompressionType.ZLIB:
                if self.decompressor:
                    decompressed = self.decompressor.decompress(data)
                    return decompressed
                else:
                    return data
            
            elif self.compression_type == CompressionType.SNAPPY:
                try:
                    import snappy
                    return snappy.decompress(data)
                except ImportError:
                    logger.warning("Snappy не доступен, данные не могут быть распакованы")
                    return data
            
            elif self.compression_type == CompressionType.LZ4:
                try:
                    import lz4.frame
                    return lz4.frame.decompress(data)
                except ImportError:
                    logger.warning("LZ4 не доступен, данные не могут быть распакованы")
                    return data
            
            return data
            
        except Exception as e:
            logger.error(f"Ошибка распаковки данных: {e}")
            return data
    
    def create_compression_header(self, data: bytes, was_compressed: bool) -> bytes:
        """
        Создание заголовка сжатия
        
        Args:
            data: Данные
            was_compressed: Были ли данные сжаты
            
        Returns:
            bytes: Заголовок сжатия
        """
        try:
            header = struct.pack('>B', self.compression_type.value)  # Тип сжатия
            header += struct.pack('>B', 1 if was_compressed else 0)  # Флаг сжатия
            header += struct.pack('>I', len(data))  # Размер данных
            
            return header
            
        except Exception as e:
            logger.error(f"Ошибка создания заголовка сжатия: {e}")
            return b''
    
    def parse_compression_header(self, header: bytes) -> Tuple[CompressionType, bool, int]:
        """
        Парсинг заголовка сжатия
        
        Args:
            header: Заголовок сжатия
            
        Returns:
            Tuple[CompressionType, bool, int]: (тип сжатия, флаг сжатия, размер данных)
        """
        try:
            if len(header) < 6:
                return CompressionType.NONE, False, 0
            
            compression_type = CompressionType(struct.unpack('>B', header[0:1])[0])
            was_compressed = bool(struct.unpack('>B', header[1:2])[0])
            data_size = struct.unpack('>I', header[2:6])[0]
            
            return compression_type, was_compressed, data_size
            
        except Exception as e:
            logger.error(f"Ошибка парсинга заголовка сжатия: {e}")
            return CompressionType.NONE, False, 0
    
    def compress_packet(self, packet_data: bytes, threshold: int = 1024) -> bytes:
        """
        Сжатие пакета Minecraft
        
        Args:
            packet_data: Данные пакета
            threshold: Минимальный размер для сжатия
            
        Returns:
            bytes: Сжатый пакет с заголовком
        """
        try:
            # Сжатие данных
            compressed_data, was_compressed = self.compress_data(packet_data, threshold)
            
            # Создание заголовка
            header = self.create_compression_header(compressed_data, was_compressed)
            
            # Объединение заголовка и данных
            return header + compressed_data
            
        except Exception as e:
            logger.error(f"Ошибка сжатия пакета: {e}")
            return packet_data
    
    def decompress_packet(self, packet_data: bytes) -> bytes:
        """
        Распаковка пакета Minecraft
        
        Args:
            packet_data: Сжатый пакет
            
        Returns:
            bytes: Распакованные данные
        """
        try:
            if len(packet_data) < 6:
                return packet_data
            
            # Парсинг заголовка
            compression_type, was_compressed, data_size = self.parse_compression_header(packet_data[:6])
            
            if not was_compressed:
                return packet_data[6:]
            
            # Распаковка данных
            compressed_data = packet_data[6:6+data_size]
            decompressed_data = self.decompress_data(compressed_data, was_compressed)
            
            return decompressed_data
            
        except Exception as e:
            logger.error(f"Ошибка распаковки пакета: {e}")
            return packet_data
    
    def get_compression_stats(self) -> dict:
        """
        Получение статистики сжатия
        
        Returns:
            dict: Статистика сжатия
        """
        return {
            'compression_type': self.compression_type.name,
            'compression_level': self.compression_level,
            'compressor_available': self.compressor is not None,
            'decompressor_available': self.decompressor is not None
        }
    
    def reset_compressors(self):
        """Сброс компрессоров"""
        try:
            if self.compression_type == CompressionType.ZLIB:
                self.compressor = zlib.compressobj(self.compression_level)
                self.decompressor = zlib.decompressobj()
            
            logger.info("Компрессоры сброшены")
            
        except Exception as e:
            logger.error(f"Ошибка сброса компрессоров: {e}")
    
    def change_compression_type(self, new_type: CompressionType, level: int = 6):
        """
        Изменение типа сжатия
        
        Args:
            new_type: Новый тип сжатия
            level: Уровень сжатия
        """
        try:
            self.compression_type = new_type
            self.compression_level = level
            
            # Переинициализация компрессоров
            self.reset_compressors()
            
            logger.info(f"Тип сжатия изменен на: {new_type.name} (уровень: {level})")
            
        except Exception as e:
            logger.error(f"Ошибка изменения типа сжатия: {e}")

class AdaptiveCompression:
    """Адаптивное сжатие на основе статистики"""
    
    def __init__(self, initial_type: CompressionType = CompressionType.ZLIB):
        self.compression_manager = CompressionManager(initial_type)
        self.stats = {
            'total_packets': 0,
            'compressed_packets': 0,
            'total_original_size': 0,
            'total_compressed_size': 0,
            'compression_ratio': 1.0
        }
        
        logger.info("Адаптивное сжатие инициализировано")
    
    def compress_packet_adaptive(self, packet_data: bytes) -> bytes:
        """
        Адаптивное сжатие пакета
        
        Args:
            packet_data: Данные пакета
            
        Returns:
            bytes: Сжатый пакет
        """
        try:
            original_size = len(packet_data)
            
            # Сжатие с текущими настройками
            compressed_packet = self.compression_manager.compress_packet(packet_data)
            compressed_size = len(compressed_packet)
            
            # Обновление статистики
            self.stats['total_packets'] += 1
            self.stats['total_original_size'] += original_size
            self.stats['total_compressed_size'] += compressed_size
            
            if compressed_size < original_size:
                self.stats['compressed_packets'] += 1
            
            # Расчет коэффициента сжатия
            if self.stats['total_original_size'] > 0:
                self.stats['compression_ratio'] = (
                    self.stats['total_compressed_size'] / self.stats['total_original_size']
                )
            
            # Адаптивная настройка
            self._adapt_compression_settings()
            
            return compressed_packet
            
        except Exception as e:
            logger.error(f"Ошибка адаптивного сжатия: {e}")
            return packet_data
    
    def _adapt_compression_settings(self):
        """Адаптивная настройка параметров сжатия"""
        try:
            # Если коэффициент сжатия плохой, пробуем другой тип
            if self.stats['compression_ratio'] > 0.9 and self.stats['total_packets'] > 100:
                current_type = self.compression_manager.compression_type
                
                if current_type == CompressionType.ZLIB:
                    # Пробуем LZ4
                    self.compression_manager.change_compression_type(CompressionType.LZ4, 1)
                    logger.info("Переключение на LZ4 из-за плохого сжатия")
                
                elif current_type == CompressionType.LZ4:
                    # Пробуем Snappy
                    self.compression_manager.change_compression_type(CompressionType.SNAPPY)
                    logger.info("Переключение на Snappy из-за плохого сжатия")
                
                elif current_type == CompressionType.SNAPPY:
                    # Возвращаемся к ZLIB с высоким уровнем
                    self.compression_manager.change_compression_type(CompressionType.ZLIB, 9)
                    logger.info("Переключение на ZLIB с высоким уровнем сжатия")
            
            # Сброс статистики каждые 1000 пакетов
            if self.stats['total_packets'] > 1000:
                self._reset_stats()
                
        except Exception as e:
            logger.error(f"Ошибка адаптивной настройки: {e}")
    
    def _reset_stats(self):
        """Сброс статистики"""
        self.stats = {
            'total_packets': 0,
            'compressed_packets': 0,
            'total_original_size': 0,
            'total_compressed_size': 0,
            'compression_ratio': 1.0
        }
        logger.debug("Статистика сжатия сброшена")
    
    def get_compression_stats(self) -> dict:
        """
        Получение статистики адаптивного сжатия
        
        Returns:
            dict: Статистика сжатия
        """
        stats = self.compression_manager.get_compression_stats()
        stats.update(self.stats)
        return stats