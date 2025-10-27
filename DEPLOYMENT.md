# 🚀 Руководство по развертыванию

Это руководство поможет вам развернуть Telegram бота "Орёл или решка" на различных платформах.

## 📋 Предварительные требования

- Python 3.8 или выше
- Telegram Bot Token (получите у [@BotFather](https://t.me/BotFather))
- Доступ к серверу или хостинг-платформе

## 🖥️ Локальное развертывание

### 1. Клонирование и настройка

```bash
# Клонируем репозиторий
git clone <repository-url>
cd telegram-coin-flip-bot

# Создаем виртуальное окружение
python -m venv venv

# Активируем виртуальное окружение
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Устанавливаем зависимости
pip install -r requirements.txt
```

### 2. Настройка конфигурации

```bash
# Копируем файл конфигурации
cp .env.example .env

# Редактируем .env файл
nano .env
```

Добавьте ваш токен бота:
```env
BOT_TOKEN=your_actual_bot_token_here
```

### 3. Запуск бота

```bash
# Запуск через основной файл
python bot.py

# Или через runner
python run.py
```

## ☁️ Развертывание на VPS/Сервере

### 1. Подготовка сервера

```bash
# Обновляем систему
sudo apt update && sudo apt upgrade -y

# Устанавливаем Python и pip
sudo apt install python3 python3-pip python3-venv -y

# Устанавливаем git
sudo apt install git -y
```

### 2. Развертывание приложения

```bash
# Клонируем репозиторий
git clone <repository-url>
cd telegram-coin-flip-bot

# Создаем виртуальное окружение
python3 -m venv venv
source venv/bin/activate

# Устанавливаем зависимости
pip install -r requirements.txt

# Настраиваем конфигурацию
cp .env.example .env
nano .env
```

### 3. Запуск с nohup

```bash
# Запускаем бота в фоне
nohup python3 run.py > bot.log 2>&1 &

# Проверяем статус
ps aux | grep python3
tail -f bot.log
```

### 4. Настройка systemd (рекомендуется)

Создайте файл сервиса:

```bash
sudo nano /etc/systemd/system/coin-flip-bot.service
```

Содержимое файла:
```ini
[Unit]
Description=Telegram Coin Flip Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/telegram-coin-flip-bot
Environment=PATH=/path/to/telegram-coin-flip-bot/venv/bin
ExecStart=/path/to/telegram-coin-flip-bot/venv/bin/python run.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Активируйте сервис:

```bash
# Перезагружаем systemd
sudo systemctl daemon-reload

# Включаем автозапуск
sudo systemctl enable coin-flip-bot

# Запускаем сервис
sudo systemctl start coin-flip-bot

# Проверяем статус
sudo systemctl status coin-flip-bot

# Просматриваем логи
sudo journalctl -u coin-flip-bot -f
```

## 🐳 Развертывание с Docker

### 1. Создание Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Копируем файлы зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY . .

# Создаем пользователя для безопасности
RUN useradd -m -u 1000 botuser && chown -R botuser:botuser /app
USER botuser

# Запускаем бота
CMD ["python", "run.py"]
```

### 2. Создание docker-compose.yml

```yaml
version: '3.8'

services:
  coin-flip-bot:
    build: .
    container_name: coin-flip-bot
    restart: unless-stopped
    environment:
      - BOT_TOKEN=${BOT_TOKEN}
    volumes:
      - ./logs:/app/logs
      - ./game_database.db:/app/game_database.db
    networks:
      - bot-network

networks:
  bot-network:
    driver: bridge
```

### 3. Запуск с Docker

```bash
# Создаем .env файл
cp .env.example .env
nano .env

# Собираем и запускаем
docker-compose up -d

# Проверяем логи
docker-compose logs -f
```

## 🌐 Развертывание на облачных платформах

### Heroku

1. Создайте `Procfile`:
```
worker: python run.py
```

2. Создайте `runtime.txt`:
```
python-3.9.18
```

3. Развертывание:
```bash
# Устанавливаем Heroku CLI
# Создаем приложение
heroku create your-bot-name

# Добавляем переменные окружения
heroku config:set BOT_TOKEN=your_bot_token

# Развертываем
git push heroku main

# Запускаем worker
heroku ps:scale worker=1
```

### Railway

1. Подключите GitHub репозиторий к Railway
2. Добавьте переменную окружения `BOT_TOKEN`
3. Railway автоматически развернет приложение

### Render

1. Создайте новый Web Service
2. Подключите GitHub репозиторий
3. Настройте:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python run.py`
4. Добавьте переменную окружения `BOT_TOKEN`

## 🔧 Настройка Nginx (опционально)

Если вы хотите добавить веб-интерфейс для мониторинга:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 📊 Мониторинг и логирование

### Настройка логирования

В файле `config.py` можно настроить уровень логирования:

```python
import logging

# Для продакшена
logging.basicConfig(level=logging.WARNING)

# Для разработки
logging.basicConfig(level=logging.DEBUG)
```

### Мониторинг состояния

Создайте скрипт для проверки состояния бота:

```bash
#!/bin/bash
# check_bot.sh

if ! pgrep -f "python.*run.py" > /dev/null; then
    echo "Bot is down! Restarting..."
    cd /path/to/telegram-coin-flip-bot
    source venv/bin/activate
    nohup python run.py > bot.log 2>&1 &
fi
```

Добавьте в crontab:
```bash
# Проверка каждые 5 минут
*/5 * * * * /path/to/check_bot.sh
```

## 🔒 Безопасность

### Рекомендации по безопасности:

1. **Никогда не коммитьте токен бота** в репозиторий
2. Используйте **виртуальные окружения**
3. Регулярно **обновляйте зависимости**
4. Настройте **файрвол** на сервере
5. Используйте **HTTPS** для веб-интерфейса
6. Ограничьте **доступ к базе данных**

### Обновление зависимостей:

```bash
# Проверка уязвимостей
pip-audit

# Обновление зависимостей
pip install --upgrade -r requirements.txt
```

## 🚨 Устранение неполадок

### Частые проблемы:

1. **Бот не отвечает**
   - Проверьте логи: `tail -f logs/bot.log`
   - Убедитесь, что токен правильный
   - Проверьте интернет-соединение

2. **Ошибки базы данных**
   - Проверьте права доступа к файлу БД
   - Убедитесь, что директория доступна для записи

3. **Проблемы с зависимостями**
   - Обновите pip: `pip install --upgrade pip`
   - Переустановите зависимости: `pip install -r requirements.txt --force-reinstall`

4. **Проблемы с systemd**
   - Проверьте статус: `sudo systemctl status coin-flip-bot`
   - Просмотрите логи: `sudo journalctl -u coin-flip-bot -f`

## 📞 Поддержка

Если у вас возникли проблемы с развертыванием:

1. Проверьте логи приложения
2. Убедитесь, что все зависимости установлены
3. Проверьте настройки окружения
4. Создайте Issue в репозитории с подробным описанием проблемы

---

**Удачного развертывания! 🚀**