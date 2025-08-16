# 🔧 Подробное руководство по настройке

Это руководство содержит детальные инструкции по настройке Telegram бота "Орёл или решка" для различных сценариев использования.

## 📋 Содержание

1. [Предварительные требования](#предварительные-требования)
2. [Установка и настройка](#установка-и-настройка)
3. [Конфигурация бота](#конфигурация-бота)
4. [Настройка базы данных](#настройка-базы-данных)
5. [Настройка логирования](#настройка-логирования)
6. [Безопасность](#безопасность)
7. [Тестирование](#тестирование)
8. [Мониторинг](#мониторинг)

## 🎯 Предварительные требования

### Системные требования

**Минимальные:**
- Python 3.8+
- 512 MB RAM
- 100 MB свободного места
- Стабильное интернет-соединение

**Рекомендуемые:**
- Python 3.9+
- 1 GB RAM
- 500 MB свободного места
- Высокоскоростное интернет-соединение

### Программное обеспечение

**Обязательное:**
- Python 3.8 или выше
- pip (менеджер пакетов Python)
- Git (для клонирования репозитория)

**Опциональное:**
- Docker (для контейнеризации)
- SQLite (включен в Python)
- Nginx (для веб-интерфейса)

## 🚀 Установка и настройка

### Шаг 1: Подготовка окружения

#### Windows:
```cmd
# Проверяем версию Python
python --version

# Устанавливаем Git (если не установлен)
# Скачайте с https://git-scm.com/download/win

# Создаем рабочую директорию
mkdir telegram-bots
cd telegram-bots
```

#### Linux (Ubuntu/Debian):
```bash
# Обновляем систему
sudo apt update && sudo apt upgrade -y

# Устанавливаем необходимые пакеты
sudo apt install python3 python3-pip python3-venv git curl wget -y

# Проверяем версию Python
python3 --version
```

#### macOS:
```bash
# Устанавливаем Homebrew (если не установлен)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Устанавливаем Python
brew install python3

# Проверяем версию
python3 --version
```

### Шаг 2: Клонирование проекта

```bash
# Клонируем репозиторий
git clone <repository-url>
cd telegram-coin-flip-bot

# Проверяем структуру проекта
ls -la
```

### Шаг 3: Создание виртуального окружения

```bash
# Создаем виртуальное окружение
python3 -m venv venv

# Активируем виртуальное окружение
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Проверяем активацию
which python  # Должен показывать путь к venv
```

### Шаг 4: Установка зависимостей

```bash
# Обновляем pip
pip install --upgrade pip

# Устанавливаем зависимости
pip install -r requirements.txt

# Проверяем установку
pip list
```

## 🤖 Конфигурация бота

### Шаг 1: Получение токена бота

1. **Откройте Telegram**
2. **Найдите @BotFather**
3. **Отправьте команду `/newbot`**
4. **Следуйте инструкциям:**
   - Введите имя бота (например: "Орёл или решка")
   - Введите username бота (например: "my_coin_flip_bot")
5. **Скопируйте полученный токен**

### Шаг 2: Настройка переменных окружения

```bash
# Копируем файл конфигурации
cp .env.example .env

# Редактируем файл
nano .env  # или любой текстовый редактор
```

**Содержимое .env файла:**
```env
# Основные настройки
BOT_TOKEN=your_actual_bot_token_here

# Настройки игры
MIN_BET=1
MAX_BET=1000
DUEL_TIMEOUT=60
GAME_TIMEOUT=30

# Настройки логирования
LOG_LEVEL=INFO
LOG_FILE=bot.log

# Настройки базы данных
DB_PATH=game_database.db

# Дополнительные настройки
DEBUG=False
CLEANUP_INTERVAL=300
```

### Шаг 3: Настройка бота в Telegram

Отправьте BotFather следующие команды:

#### Установка команд:
```
/setcommands
```
```
start - Начать игру
help - Правила и помощь
stats - Ваша статистика
balance - Ваш баланс
```

#### Установка описания:
```
/setdescription
```
```
🎮 Игра "Орёл или решка" с возможностью дуэлей!
💰 Виртуальные ставки, статистика, достижения
⚔️ Сражайтесь с друзьями в дуэлях
📊 Отслеживайте свой прогресс
```

#### Установка информации:
```
/setabouttext
```
```
🎮 Игровой бот "Орёл или решка"
🎯 Играйте с ботом или в дуэлях
💰 Виртуальная валюта и статистика
📱 Работает на всех устройствах
```

## 🗄️ Настройка базы данных

### Автоматическая настройка

База данных SQLite создается автоматически при первом запуске бота.

### Ручная настройка (опционально)

```bash
# Создаем директорию для данных
mkdir data

# Инициализируем базу данных
python3 -c "
from database import Database
db = Database('data/game_database.db')
print('База данных создана успешно')
"
```

### Настройка прав доступа (Linux/macOS)

```bash
# Устанавливаем правильные права
chmod 644 data/game_database.db
chmod 755 data/

# Проверяем права
ls -la data/
```

## 📝 Настройка логирования

### Базовая настройка

Логирование настраивается в файле `run.py`:

```python
def setup_logging():
    """Настройка логирования"""
    # Создаем директорию для логов если её нет
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Настраиваем логирование
    logging.basicConfig(
        level=logging.INFO,  # Уровень логирования
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "bot.log", encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
```

### Настройка уровней логирования

```python
# Для разработки
logging.basicConfig(level=logging.DEBUG)

# Для продакшена
logging.basicConfig(level=logging.WARNING)

# Для отладки
logging.basicConfig(level=logging.ERROR)
```

### Ротация логов (опционально)

```python
from logging.handlers import RotatingFileHandler

# Создаем ротацию логов
handler = RotatingFileHandler(
    'logs/bot.log',
    maxBytes=1024*1024,  # 1MB
    backupCount=5,
    encoding='utf-8'
)
```

## 🔒 Безопасность

### Защита токена бота

1. **Никогда не коммитьте токен в репозиторий**
2. **Используйте .env файл**
3. **Добавьте .env в .gitignore**

```bash
# Проверяем .gitignore
cat .gitignore

# Должно содержать:
# .env
# *.db
# logs/
# __pycache__/
```

### Настройка файрвола (Linux)

```bash
# Устанавливаем ufw
sudo apt install ufw

# Включаем файрвол
sudo ufw enable

# Разрешаем SSH
sudo ufw allow ssh

# Разрешаем HTTP/HTTPS (если нужно)
sudo ufw allow 80
sudo ufw allow 443

# Проверяем статус
sudo ufw status
```

### Настройка пользователя (Linux)

```bash
# Создаем пользователя для бота
sudo useradd -m -s /bin/bash botuser

# Передаем права на директорию
sudo chown -R botuser:botuser /path/to/telegram-coin-flip-bot

# Переключаемся на пользователя
sudo su - botuser
```

## 🧪 Тестирование

### Запуск тестов

```bash
# Запускаем все тесты
python3 test_bot.py

# Запускаем с подробным выводом
python3 -m unittest test_bot.py -v

# Запускаем конкретный тест
python3 -m unittest test_bot.TestGameLogic.test_flip_coin -v
```

### Ручное тестирование

```bash
# Запускаем бота в тестовом режиме
DEBUG=True python3 run.py

# Проверяем логи
tail -f logs/bot.log
```

### Тестирование базы данных

```bash
# Проверяем структуру БД
sqlite3 game_database.db ".schema"

# Проверяем данные
sqlite3 game_database.db "SELECT COUNT(*) FROM players;"
sqlite3 game_database.db "SELECT COUNT(*) FROM games;"
```

## 📊 Мониторинг

### Настройка мониторинга состояния

```bash
# Создаем скрипт мониторинга
cat > monitor_bot.sh << 'EOF'
#!/bin/bash

BOT_DIR="/path/to/telegram-coin-flip-bot"
LOG_FILE="$BOT_DIR/logs/monitor.log"

# Проверяем процесс
if ! pgrep -f "python.*run.py" > /dev/null; then
    echo "$(date): Bot is down! Restarting..." >> $LOG_FILE
    cd $BOT_DIR
    source venv/bin/activate
    nohup python run.py > bot.log 2>&1 &
    echo "$(date): Bot restarted" >> $LOG_FILE
else
    echo "$(date): Bot is running" >> $LOG_FILE
fi

# Проверяем размер логов
LOG_SIZE=$(du -m logs/bot.log | cut -f1)
if [ $LOG_SIZE -gt 100 ]; then
    echo "$(date): Log file is too large ($LOG_SIZE MB)" >> $LOG_FILE
    mv logs/bot.log logs/bot.log.old
    touch logs/bot.log
fi
EOF

chmod +x monitor_bot.sh
```

### Настройка автоматического мониторинга

```bash
# Добавляем в crontab
crontab -e

# Добавляем строки:
# Проверка каждые 5 минут
*/5 * * * * /path/to/monitor_bot.sh

# Очистка старых логов каждый день в 2:00
0 2 * * * find /path/to/logs -name "*.log.old" -mtime +7 -delete
```

### Настройка уведомлений

```bash
# Создаем скрипт уведомлений
cat > notify_admin.sh << 'EOF'
#!/bin/bash

ADMIN_ID="your_telegram_id"
BOT_TOKEN="your_bot_token"

send_notification() {
    local message="$1"
    curl -s "https://api.telegram.org/bot$BOT_TOKEN/sendMessage" \
         -d "chat_id=$ADMIN_ID" \
         -d "text=$message" \
         -d "parse_mode=HTML"
}

# Проверяем статус бота
if ! pgrep -f "python.*run.py" > /dev/null; then
    send_notification "🚨 <b>ВНИМАНИЕ!</b>\n\nБот остановлен и требует перезапуска!"
fi
EOF

chmod +x notify_admin.sh
```

## 🔧 Дополнительные настройки

### Настройка производительности

```python
# В config.py
import os

# Настройки производительности
MAX_CONCURRENT_GAMES = 100
MAX_CONCURRENT_DUELS = 50
CLEANUP_INTERVAL = 300  # 5 минут
```

### Настройка резервного копирования

```bash
# Создаем скрипт резервного копирования
cat > backup.sh << 'EOF'
#!/bin/bash

BACKUP_DIR="/path/to/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Создаем резервную копию БД
cp game_database.db "$BACKUP_DIR/game_database_$DATE.db"

# Создаем резервную копию логов
tar -czf "$BACKUP_DIR/logs_$DATE.tar.gz" logs/

# Удаляем старые резервные копии (старше 30 дней)
find $BACKUP_DIR -name "*.db" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
EOF

chmod +x backup.sh
```

### Настройка обновлений

```bash
# Создаем скрипт обновления
cat > update_bot.sh << 'EOF'
#!/bin/bash

BOT_DIR="/path/to/telegram-coin-flip-bot"

cd $BOT_DIR

# Останавливаем бота
pkill -f "python.*run.py"

# Обновляем код
git pull origin main

# Обновляем зависимости
source venv/bin/activate
pip install -r requirements.txt --upgrade

# Запускаем бота
nohup python run.py > bot.log 2>&1 &

echo "Bot updated and restarted"
EOF

chmod +x update_bot.sh
```

## 🎯 Проверка установки

### Финальная проверка

```bash
# Проверяем структуру проекта
tree -I 'venv|__pycache__|*.pyc'

# Проверяем зависимости
pip list

# Проверяем конфигурацию
python3 -c "from config import BOT_TOKEN; print('Token configured:', bool(BOT_TOKEN))"

# Проверяем базу данных
python3 -c "from database import Database; db = Database(); print('Database OK')"

# Запускаем тесты
python3 test_bot.py
```

### Проверка работоспособности

1. **Запустите бота:** `python3 run.py`
2. **Отправьте `/start` боту в Telegram**
3. **Протестируйте основные функции:**
   - Игра с ботом
   - Создание дуэли
   - Просмотр статистики
4. **Проверьте логи:** `tail -f logs/bot.log`

## 📞 Поддержка

### Получение помощи

1. **Проверьте логи:** `tail -f logs/bot.log`
2. **Запустите тесты:** `python3 test_bot.py`
3. **Проверьте документацию:** `README.md`
4. **Создайте Issue** в репозитории

### Полезные команды

```bash
# Проверка статуса
ps aux | grep python

# Просмотр логов
tail -f logs/bot.log

# Проверка БД
sqlite3 game_database.db ".tables"

# Очистка кэша
find . -name "*.pyc" -delete
find . -name "__pycache__" -delete
```

---

**Удачной настройки! 🚀**