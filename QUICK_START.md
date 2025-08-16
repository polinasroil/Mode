# ⚡ Быстрый старт

Этот файл поможет вам быстро запустить Telegram бота "Орёл или решка" за 5 минут!

## 🚀 Быстрая установка

### Шаг 1: Получение токена бота
1. Откройте Telegram
2. Найдите [@BotFather](https://t.me/BotFather)
3. Отправьте `/newbot`
4. Следуйте инструкциям и получите токен

### Шаг 2: Клонирование и настройка
```bash
# Клонируем проект
git clone <repository-url>
cd telegram-coin-flip-bot

# Создаем виртуальное окружение
python -m venv venv

# Активируем (Windows)
venv\Scripts\activate
# Активируем (Linux/Mac)
source venv/bin/activate

# Устанавливаем зависимости
pip install -r requirements.txt
```

### Шаг 3: Настройка конфигурации
```bash
# Копируем файл конфигурации
cp .env.example .env

# Редактируем файл (замените на ваш токен)
echo "BOT_TOKEN=your_actual_bot_token_here" > .env
```

### Шаг 4: Запуск бота
```bash
# Запускаем бота
python run.py
```

## 🎮 Как играть

### Игра с ботом:
1. Отправьте `/start` боту
2. Выберите "🎮 Игра с ботом"
3. Выберите ставку (10, 25, 50, 100, 250, 500, 1000 или своя)
4. Выберите сторону монеты (Орёл или Решка)
5. Получите результат!

### Дуэли:
1. Выберите "⚔️ Создать дуэль"
2. Отправьте ссылку другу
3. Оба игрока делают ставки
4. Оба выбирают сторону монеты
5. Победитель забирает все!

## 📱 Команды бота

- `/start` - начать игру
- `/help` - правила и помощь
- `/stats` - ваша статистика
- `/balance` - ваш баланс

## ⚙️ Быстрые настройки

### Изменение ставок:
Отредактируйте `config.py`:
```python
MIN_BET = 1      # Минимальная ставка
MAX_BET = 1000   # Максимальная ставка
```

### Изменение времени ожидания:
```python
DUEL_TIMEOUT = 60  # Время ожидания дуэли (секунды)
GAME_TIMEOUT = 30  # Время ожидания в игре (секунды)
```

## 🔧 Быстрое развертывание

### На VPS (Ubuntu/Debian):
```bash
# Обновляем систему
sudo apt update && sudo apt upgrade -y

# Устанавливаем Python
sudo apt install python3 python3-pip python3-venv git -y

# Клонируем и настраиваем
git clone <repository-url>
cd telegram-coin-flip-bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Настраиваем конфигурацию
cp .env.example .env
nano .env  # Вставьте ваш токен

# Запускаем в фоне
nohup python3 run.py > bot.log 2>&1 &
```

### С Docker:
```bash
# Создаем .env файл
cp .env.example .env
echo "BOT_TOKEN=your_token" > .env

# Запускаем с Docker
docker-compose up -d
```

## 🐛 Быстрое устранение проблем

### Бот не отвечает:
```bash
# Проверяем логи
tail -f logs/bot.log

# Проверяем токен
cat .env | grep BOT_TOKEN
```

### Ошибки зависимостей:
```bash
# Переустанавливаем зависимости
pip install -r requirements.txt --force-reinstall
```

### Проблемы с базой данных:
```bash
# Проверяем права доступа
ls -la game_database.db

# Пересоздаем базу (осторожно - потеряете данные)
rm game_database.db
python run.py
```

## 📊 Мониторинг

### Проверка статуса:
```bash
# Проверяем процесс
ps aux | grep python

# Проверяем логи
tail -f logs/bot.log
```

### Автоматический перезапуск:
```bash
# Создаем скрипт мониторинга
cat > check_bot.sh << 'EOF'
#!/bin/bash
if ! pgrep -f "python.*run.py" > /dev/null; then
    echo "Bot is down! Restarting..."
    cd /path/to/telegram-coin-flip-bot
    source venv/bin/activate
    nohup python run.py > bot.log 2>&1 &
fi
EOF

chmod +x check_bot.sh

# Добавляем в crontab (проверка каждые 5 минут)
crontab -e
# Добавьте строку: */5 * * * * /path/to/check_bot.sh
```

## 🎯 Готово!

Теперь ваш бот готов к работе! 

### Что дальше:
1. Протестируйте бота в Telegram
2. Настройте дополнительные параметры в `config.py`
3. Изучите полную документацию в `README.md`
4. Настройте мониторинг и логирование

### Полезные ссылки:
- 📖 [Полная документация](README.md)
- 🚀 [Руководство по развертыванию](DEPLOYMENT.md)
- 🧪 [Запуск тестов](test_bot.py)

---

**Удачной игры! 🍀**