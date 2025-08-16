#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Minecraft PE Server - Веб-панель управления
Автор: Minecraft PE Server Team
Версия: 1.0.0
"""

import json
import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import psutil

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Инициализация Flask приложения
app = Flask(__name__)
app.secret_key = 'minecraft_pe_server_secret_key_2024'

# Настройки Flask
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# Инициализация Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Загрузка конфигурации
def load_config():
    """Загрузка конфигурации веб-панели"""
    config_path = Path("../config/web-panel.properties")
    config = {}
    
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip()
    
    # Значения по умолчанию
    defaults = {
        'web-port': '8080',
        'web-host': '0.0.0.0',
        'admin-username': 'admin',
        'admin-password': 'admin123',
        'theme': 'dark',
        'language': 'ru'
    }
    
    for key, value in defaults.items():
        if key not in config:
            config[key] = value
    
    return config

config = load_config()

# Модель пользователя
class User(UserMixin):
    def __init__(self, username, password_hash, role='admin'):
        self.id = username
        self.username = username
        self.password_hash = password_hash
        self.role = role

# Простое хранилище пользователей (в продакшене использовать базу данных)
users = {
    config['admin-username']: User(
        config['admin-username'],
        generate_password_hash(config['admin-password']),
        'admin'
    )
}

@login_manager.user_loader
def load_user(user_id):
    return users.get(user_id)

# Маршруты аутентификации
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = users.get(username)
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            session.permanent = True
            return redirect(url_for('dashboard'))
        else:
            flash('Неверное имя пользователя или пароль', 'error')
    
    return render_template('login.html', config=config)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Основные маршруты
@app.route('/')
@login_required
def dashboard():
    """Главная панель управления"""
    server_info = get_server_info()
    system_info = get_system_info()
    
    return render_template('dashboard.html', 
                         server_info=server_info, 
                         system_info=system_info,
                         config=config)

@app.route('/players')
@login_required
def players():
    """Управление игроками"""
    players_data = get_players_data()
    return render_template('players.html', players=players_data, config=config)

@app.route('/worlds')
@login_required
def worlds():
    """Управление мирами"""
    worlds_data = get_worlds_data()
    return render_template('worlds.html', worlds=worlds_data, config=config)

@app.route('/plugins')
@login_required
def plugins():
    """Управление плагинами"""
    plugins_data = get_plugins_data()
    return render_template('plugins.html', plugins=plugins_data, config=config)

@app.route('/console')
@login_required
def console():
    """Консоль сервера"""
    console_data = get_console_data()
    return render_template('console.html', console_data=console_data, config=config)

@app.route('/settings')
@login_required
def settings():
    """Настройки сервера"""
    server_settings = get_server_settings()
    return render_template('settings.html', settings=server_settings, config=config)

@app.route('/backups')
@login_required
def backups():
    """Управление резервными копиями"""
    backups_data = get_backups_data()
    return render_template('backups.html', backups=backups_data, config=config)

# API маршруты
@app.route('/api/server/status')
@login_required
def api_server_status():
    """API для получения статуса сервера"""
    try:
        status = {
            'running': is_server_running(),
            'uptime': get_server_uptime(),
            'players_online': get_online_players_count(),
            'max_players': get_max_players(),
            'tps': get_server_tps(),
            'memory_usage': get_memory_usage(),
            'cpu_usage': get_cpu_usage()
        }
        return jsonify(status)
    except Exception as e:
        logger.error(f"Ошибка получения статуса сервера: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/server/start', methods=['POST'])
@login_required
def api_server_start():
    """API для запуска сервера"""
    try:
        if start_server():
            return jsonify({'success': True, 'message': 'Сервер запущен'})
        else:
            return jsonify({'success': False, 'message': 'Не удалось запустить сервер'}), 500
    except Exception as e:
        logger.error(f"Ошибка запуска сервера: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/server/stop', methods=['POST'])
@login_required
def api_server_stop():
    """API для остановки сервера"""
    try:
        if stop_server():
            return jsonify({'success': True, 'message': 'Сервер остановлен'})
        else:
            return jsonify({'success': False, 'message': 'Не удалось остановить сервер'}), 500
    except Exception as e:
        logger.error(f"Ошибка остановки сервера: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/server/restart', methods=['POST'])
@login_required
def api_server_restart():
    """API для перезапуска сервера"""
    try:
        if restart_server():
            return jsonify({'success': True, 'message': 'Сервер перезапущен'})
        else:
            return jsonify({'success': False, 'message': 'Не удалось перезапустить сервер'}), 500
    except Exception as e:
        logger.error(f"Ошибка перезапуска сервера: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/players')
@login_required
def api_players():
    """API для получения списка игроков"""
    try:
        players = get_players_data()
        return jsonify(players)
    except Exception as e:
        logger.error(f"Ошибка получения списка игроков: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/players/<username>/kick', methods=['POST'])
@login_required
def api_player_kick(username):
    """API для кика игрока"""
    try:
        if kick_player(username):
            return jsonify({'success': True, 'message': f'Игрок {username} кикнут'})
        else:
            return jsonify({'success': False, 'message': f'Не удалось кикнуть игрока {username}'}), 500
    except Exception as e:
        logger.error(f"Ошибка кика игрока {username}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/players/<username>/ban', methods=['POST'])
@login_required
def api_player_ban(username):
    """API для бана игрока"""
    try:
        reason = request.json.get('reason', 'Нарушение правил')
        if ban_player(username, reason):
            return jsonify({'success': True, 'message': f'Игрок {username} забанен'})
        else:
            return jsonify({'success': False, 'message': f'Не удалось забанить игрока {username}'}), 500
    except Exception as e:
        logger.error(f"Ошибка бана игрока {username}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/console/command', methods=['POST'])
@login_required
def api_console_command():
    """API для выполнения команды в консоли"""
    try:
        command = request.json.get('command', '')
        if not command:
            return jsonify({'error': 'Команда не указана'}), 400
        
        result = execute_console_command(command)
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        logger.error(f"Ошибка выполнения команды: {e}")
        return jsonify({'error': str(e)}), 500

# Функции для работы с сервером
def is_server_running():
    """Проверка, запущен ли сервер"""
    try:
        # Проверка процесса по порту
        for conn in psutil.net_connections():
            if conn.laddr.port == int(config.get('web-port', 8080)):
                return True
        return False
    except:
        return False

def get_server_info():
    """Получение информации о сервере"""
    return {
        'name': 'Minecraft PE Server',
        'version': '1.0.0',
        'status': 'running' if is_server_running() else 'stopped',
        'uptime': get_server_uptime(),
        'players_online': get_online_players_count(),
        'max_players': get_max_players()
    }

def get_system_info():
    """Получение системной информации"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            'cpu_usage': cpu_percent,
            'memory_total': memory.total // (1024**3),  # GB
            'memory_used': memory.used // (1024**3),   # GB
            'memory_percent': memory.percent,
            'disk_total': disk.total // (1024**3),     # GB
            'disk_used': disk.used // (1024**3),       # GB
            'disk_percent': (disk.used / disk.total) * 100
        }
    except:
        return {}

def get_server_uptime():
    """Получение времени работы сервера"""
    # Здесь должна быть логика получения реального uptime
    return "2h 15m 30s"

def get_online_players_count():
    """Получение количества игроков онлайн"""
    # Здесь должна быть логика получения реального количества игроков
    return 5

def get_max_players():
    """Получение максимального количества игроков"""
    return 20

def get_server_tps():
    """Получение TPS сервера"""
    return 20.0

def get_memory_usage():
    """Получение использования памяти"""
    try:
        process = psutil.Process()
        return process.memory_info().rss // (1024**2)  # MB
    except:
        return 0

def get_cpu_usage():
    """Получение использования CPU"""
    try:
        process = psutil.Process()
        return process.cpu_percent()
    except:
        return 0

def get_players_data():
    """Получение данных об игроках"""
    # Здесь должна быть логика получения реальных данных об игроках
    return [
        {
            'username': 'Player1',
            'ip_address': '192.168.1.100',
            'join_time': '2024-01-15 14:30:00',
            'last_seen': '2024-01-15 15:45:00',
            'gamemode': 'survival',
            'health': 20.0,
            'hunger': 18.0,
            'experience': 150,
            'level': 5
        },
        {
            'username': 'Player2',
            'ip_address': '192.168.1.101',
            'join_time': '2024-01-15 14:35:00',
            'last_seen': '2024-01-15 15:40:00',
            'gamemode': 'creative',
            'health': 20.0,
            'hunger': 20.0,
            'experience': 300,
            'level': 8
        }
    ]

def get_worlds_data():
    """Получение данных о мирах"""
    # Здесь должна быть логика получения реальных данных о мирах
    return [
        {
            'name': 'world',
            'seed': 12345,
            'world_type': 'default',
            'spawn_x': 0,
            'spawn_y': 64,
            'spawn_z': 0,
            'time': 12000,
            'weather': 'clear',
            'difficulty': 'normal',
            'gamemode': 'survival',
            'hardcore': False,
            'pvp': True
        }
    ]

def get_plugins_data():
    """Получение данных о плагинах"""
    # Здесь должна быть логика получения реальных данных о плагинах
    return [
        {
            'name': 'CoreProtect',
            'version': '2.0.0',
            'author': 'CoreProtect Team',
            'description': 'Логирование действий игроков',
            'enabled': True
        },
        {
            'name': 'WorldEdit',
            'version': '7.2.0',
            'author': 'WorldEdit Team',
            'description': 'Редактирование мира',
            'enabled': True
        }
    ]

def get_console_data():
    """Получение данных консоли"""
    # Здесь должна быть логика получения реальных данных консоли
    return [
        {'timestamp': '2024-01-15 15:45:00', 'level': 'INFO', 'message': 'Сервер запущен'},
        {'timestamp': '2024-01-15 15:45:01', 'level': 'INFO', 'message': 'Мир загружен'},
        {'timestamp': '2024-01-15 15:45:02', 'level': 'INFO', 'message': 'Плагины загружены'}
    ]

def get_server_settings():
    """Получение настроек сервера"""
    # Здесь должна быть логика получения реальных настроек сервера
    return {
        'server_name': 'Minecraft PE Server',
        'server_port': 19132,
        'max_players': 20,
        'gamemode': 'survival',
        'difficulty': 'normal',
        'spawn_protection': 16
    }

def get_backups_data():
    """Получение данных о резервных копиях"""
    # Здесь должна быть логика получения реальных данных о резервных копиях
    return [
        {
            'name': 'backup_20240115_143000',
            'size': '150MB',
            'created': '2024-01-15 14:30:00',
            'status': 'completed'
        }
    ]

# Функции управления сервером
def start_server():
    """Запуск сервера"""
    try:
        # Здесь должна быть логика запуска сервера
        logger.info("Сервер запущен")
        return True
    except Exception as e:
        logger.error(f"Ошибка запуска сервера: {e}")
        return False

def stop_server():
    """Остановка сервера"""
    try:
        # Здесь должна быть логика остановки сервера
        logger.info("Сервер остановлен")
        return True
    except Exception as e:
        logger.error(f"Ошибка остановки сервера: {e}")
        return False

def restart_server():
    """Перезапуск сервера"""
    try:
        if stop_server() and start_server():
            logger.info("Сервер перезапущен")
            return True
        return False
    except Exception as e:
        logger.error(f"Ошибка перезапуска сервера: {e}")
        return False

def kick_player(username):
    """Кик игрока"""
    try:
        # Здесь должна быть логика кика игрока
        logger.info(f"Игрок {username} кикнут")
        return True
    except Exception as e:
        logger.error(f"Ошибка кика игрока {username}: {e}")
        return False

def ban_player(username, reason):
    """Бан игрока"""
    try:
        # Здесь должна быть логика бана игрока
        logger.info(f"Игрок {username} забанен. Причина: {reason}")
        return True
    except Exception as e:
        logger.error(f"Ошибка бана игрока {username}: {e}")
        return False

def execute_console_command(command):
    """Выполнение команды в консоли"""
    try:
        # Здесь должна быть логика выполнения команды
        logger.info(f"Выполнена команда: {command}")
        return f"Команда '{command}' выполнена успешно"
    except Exception as e:
        logger.error(f"Ошибка выполнения команды {command}: {e}")
        return f"Ошибка выполнения команды: {e}"

# Обработка ошибок
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html', config=config), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html', config=config), 500

if __name__ == '__main__':
    try:
        port = int(config.get('web-port', 8080))
        host = config.get('web-host', '0.0.0.0')
        
        logger.info(f"Запуск веб-панели на {host}:{port}")
        app.run(host=host, port=port, debug=False)
        
    except Exception as e:
        logger.error(f"Ошибка запуска веб-панели: {e}")
        sys.exit(1)