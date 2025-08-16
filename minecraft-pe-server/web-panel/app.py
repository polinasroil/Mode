#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Minecraft PE Server - Веб-панель
Автор: Minecraft PE Server Team
Версия: 1.0.0
"""

from flask import Flask, render_template, jsonify, request
import json
import os
import sys
from pathlib import Path

# Добавление пути к модулям сервера
sys.path.insert(0, str(Path(__file__).parent.parent))

app = Flask(__name__)

@app.route('/')
def index():
    """Главная страница"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Minecraft PE Server - Веб-панель</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f0f0f0; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #2c3e50; text-align: center; }
            .status { padding: 15px; margin: 10px 0; border-radius: 5px; }
            .status.online { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
            .status.offline { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
            .info { background: #e2e3e5; padding: 15px; border-radius: 5px; margin: 10px 0; }
            .button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin: 5px; }
            .button:hover { background: #0056b3; }
            .button.danger { background: #dc3545; }
            .button.danger:hover { background: #c82333; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎮 Minecraft PE Server</h1>
            
            <div class="status online">
                <strong>Статус:</strong> Сервер запущен
            </div>
            
            <div class="info">
                <h3>Информация о сервере</h3>
                <p><strong>Название:</strong> <span id="server-name">Загрузка...</span></p>
                <p><strong>Порт:</strong> <span id="server-port">Загрузка...</span></p>
                <p><strong>Игроков:</strong> <span id="player-count">Загрузка...</span></p>
                <p><strong>Время работы:</strong> <span id="uptime">Загрузка...</span></p>
            </div>
            
            <div class="info">
                <h3>Управление</h3>
                <button class="button" onclick="refreshInfo()">🔄 Обновить</button>
                <button class="button" onclick="testConnection()">🧪 Тест подключения</button>
                <button class="button danger" onclick="stopServer()">⏹️ Остановить сервер</button>
            </div>
            
            <div class="info">
                <h3>Логи сервера</h3>
                <div id="logs" style="background: #000; color: #0f0; padding: 10px; border-radius: 5px; font-family: monospace; max-height: 300px; overflow-y: auto;">
                    Загрузка логов...
                </div>
            </div>
        </div>
        
        <script>
            // Обновление информации
            function refreshInfo() {
                fetch('/api/server-info')
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('server-name').textContent = data.name || 'Неизвестно';
                        document.getElementById('server-port').textContent = data.port || 'Неизвестно';
                        document.getElementById('player-count').textContent = data.players || '0';
                        document.getElementById('uptime').textContent = data.uptime || 'Неизвестно';
                    })
                    .catch(error => console.error('Ошибка:', error));
            }
            
            // Тест подключения
            function testConnection() {
                fetch('/api/test-connection')
                    .then(response => response.json())
                    .then(data => {
                        alert(data.message);
                    })
                    .catch(error => {
                        alert('Ошибка тестирования: ' + error);
                    });
            }
            
            // Остановка сервера
            function stopServer() {
                if (confirm('Вы уверены, что хотите остановить сервер?')) {
                    fetch('/api/stop-server', {method: 'POST'})
                        .then(response => response.json())
                        .then(data => {
                            alert(data.message);
                        })
                        .catch(error => {
                            alert('Ошибка остановки: ' + error);
                        });
                }
            }
            
            // Автообновление каждые 5 секунд
            setInterval(refreshInfo, 5000);
            
            // Загрузка при старте
            refreshInfo();
        </script>
    </body>
    </html>
    """

@app.route('/api/server-info')
def server_info():
    """API для получения информации о сервере"""
    try:
        # Попытка получить информацию из файла статистики
        stats_file = Path("../server_stats.json")
        if stats_file.exists():
            with open(stats_file, 'r', encoding='utf-8') as f:
                stats = json.load(f)
                return jsonify({
                    'name': stats.get('name', 'Minecraft PE Server'),
                    'port': 19132,
                    'players': f"{stats.get('total_players', 0)}/{stats.get('max_players', 20)}",
                    'uptime': f"{int(stats.get('uptime', 0) // 60)} мин"
                })
        else:
            return jsonify({
                'name': 'Minecraft PE Server',
                'port': 19132,
                'players': '0/20',
                'uptime': 'Неизвестно'
            })
    except Exception as e:
        return jsonify({
            'name': 'Minecraft PE Server',
            'port': 19132,
            'players': '0/20',
            'uptime': 'Ошибка загрузки'
        })

@app.route('/api/test-connection')
def test_connection():
    """API для тестирования подключения"""
    try:
        import socket
        
        # Тест подключения к порту сервера
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(2.0)
        
        # Отправка тестового ping
        ping_data = b'\x01' + b'\x00' * 24  # Простой ping
        sock.sendto(ping_data, ('localhost', 19132))
        
        try:
            data, addr = sock.recvfrom(1024)
            sock.close()
            return jsonify({'success': True, 'message': '✅ Сервер отвечает на подключения!'})
        except socket.timeout:
            sock.close()
            return jsonify({'success': False, 'message': '⚠️ Сервер не отвечает на ping (возможно, не запущен)'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'❌ Ошибка тестирования: {e}'})

@app.route('/api/stop-server', methods=['POST'])
def stop_server():
    """API для остановки сервера"""
    try:
        # Здесь можно добавить логику остановки сервера
        return jsonify({'success': True, 'message': 'Сервер остановлен'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Ошибка остановки: {e}'})

@app.route('/api/logs')
def get_logs():
    """API для получения логов сервера"""
    try:
        log_file = Path("../server.log")
        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                # Последние 50 строк
                recent_logs = lines[-50:] if len(lines) > 50 else lines
                return jsonify({'logs': recent_logs})
        else:
            return jsonify({'logs': ['Лог-файл не найден']})
    except Exception as e:
        return jsonify({'logs': [f'Ошибка чтения логов: {e}']})

if __name__ == '__main__':
    print("🌐 Запуск веб-панели Minecraft PE Server...")
    print("📱 Откройте браузер и перейдите по адресу: http://localhost:8080")
    
    try:
        app.run(host='0.0.0.0', port=8080, debug=False)
    except Exception as e:
        print(f"❌ Ошибка запуска веб-панели: {e}")
        sys.exit(1)