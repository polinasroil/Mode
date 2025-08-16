# 🚀 Настройка Telegram Бота "Орёл или решка"

Полное руководство по установке и настройке игрового бота для Telegram.

## 📋 Требования

### Системные требования:
- **Python 3.8+** (рекомендуется Python 3.11+)
- **Git** для клонирования репозитория
- **pip** для установки зависимостей
- **SQLite** (встроен в Python)

### Поддерживаемые ОС:
- ✅ **Linux** (Ubuntu, Debian, CentOS)
- ✅ **macOS** (10.14+)
- ✅ **Windows** (10/11)
- ✅ **Docker** (любая ОС)

## 🔧 Установка

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd telegram-coin-flip-bot
```

### 2. Создание виртуального окружения

#### Linux/macOS:
```bash
python3 -m venv venv
source venv/bin/activate
```

#### Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Настройка переменных окружения

1. Скопируйте файл `.env.example` в `.env`:
```bash
cp .env.example .env
```

2. Отредактируйте файл `.env`:
```env
# Обязательные настройки
BOT_TOKEN=your_actual_bot_token_here

# Опциональные настройки
MIN_BET=1
MAX_BET=1000
DUEL_TIMEOUT=60
GAME_TIMEOUT=30
LOG_LEVEL=INFO
DEBUG=False
```

### 5. Получение токена бота

1. Откройте Telegram и найдите [@BotFather](https://t.me/BotFather)
2. Отправьте команду `/newbot`
3. Следуйте инструкциям:
   - Введите имя бота (например: "Heads or Tails Game")
   - Введите username бота (например: "my_coin_flip_bot")
4. Скопируйте полученный токен в файл `.env`

## 🧪 Тестирование

### Проверка установки

Запустите тестовый скрипт:

```bash
python3 test_import.py
```

Вы должны увидеть:
```
🧪 Testing Telegram Bot 'Heads or Tails'
==================================================
Testing imports...
✓ Testing config...
✓ Testing database...
✓ Testing game_logic...
✓ Testing keyboards...
✓ Testing handlers...
✓ Testing utils...

🎉 All modules imported successfully!
✅ All tests passed! The bot is ready to run.
```

### Проверка конфигурации

```bash
python3 -c "import config; print('Config loaded successfully')"
```

## 🚀 Запуск бота

### Разработка (локальный запуск)

```bash
# Активируйте виртуальное окружение
source venv/bin/activate  # Linux/macOS
# или
venv\Scripts\activate     # Windows

# Запустите бота
python3 bot.py
```

### Продакшн (фоновый режим)

#### Linux/macOS:
```bash
nohup python3 bot.py > bot.log 2>&1 &
```

#### Windows:
```bash
pythonw bot.py
```

### Использование systemd (Linux)

1. Создайте файл службы:
```bash
sudo nano /etc/systemd/system/coin-flip-bot.service
```

2. Добавьте содержимое:
```ini
[Unit]
Description=Telegram Coin Flip Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/telegram-coin-flip-bot
Environment=PATH=/path/to/telegram-coin-flip-bot/venv/bin
ExecStart=/path/to/telegram-coin-flip-bot/venv/bin/python bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

3. Запустите службу:
```bash
sudo systemctl daemon-reload
sudo systemctl enable coin-flip-bot
sudo systemctl start coin-flip-bot
sudo systemctl status coin-flip-bot
```

## 🐳 Docker (опционально)

### Создание Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "bot.py"]
```

### Запуск с Docker

```bash
# Сборка образа
docker build -t coin-flip-bot .

# Запуск контейнера
docker run -d \
  --name coin-flip-bot \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  coin-flip-bot
```

## 📁 Структура проекта

```
telegram-coin-flip-bot/
├── bot.py              # Основной файл бота
├── config.py           # Конфигурация и сообщения
├── database.py         # Работа с базой данных
├── game_logic.py       # Игровая логика
├── keyboards.py        # Inline клавиатуры
├── handlers.py         # Обработчики текстовых сообщений
├── utils.py            # Утилиты
├── test_import.py      # Тестовый скрипт
├── requirements.txt    # Зависимости
├── .env               # Переменные окружения
├── .env.example       # Пример переменных окружения
├── README.md          # Документация
├── SETUP.md           # Инструкции по установке
├── DEPLOYMENT.md      # Инструкции по развертыванию
├── PROJECT_INFO.md    # Информация о проекте
├── QUICK_START.md     # Быстрый старт
├── LICENSE            # Лицензия
└── data/              # Данные (создается автоматически)
    └── game_database.db
```

## ⚙️ Конфигурация

### Основные настройки (config.py)

```python
# Настройки игры
MIN_BET = 1              # Минимальная ставка
MAX_BET = 1000           # Максимальная ставка
DUEL_TIMEOUT = 60        # Время ожидания дуэли (секунды)
GAME_TIMEOUT = 30        # Время ожидания в игре (секунды)
```

### Переменные окружения (.env)

```env
# Обязательные
BOT_TOKEN=your_bot_token

# Опциональные
MIN_BET=1
MAX_BET=1000
DUEL_TIMEOUT=60
GAME_TIMEOUT=30
LOG_LEVEL=INFO
LOG_FILE=bot.log
DB_PATH=game_database.db
DEBUG=False
CLEANUP_INTERVAL=300
```

## 🔍 Логирование

### Уровни логирования

- `DEBUG` - подробная отладочная информация
- `INFO` - общая информация (по умолчанию)
- `WARNING` - предупреждения
- `ERROR` - ошибки

### Просмотр логов

```bash
# В реальном времени
tail -f bot.log

# Последние 100 строк
tail -n 100 bot.log

# Поиск ошибок
grep "ERROR" bot.log
```

## 🛠️ Устранение неполадок

### Частые проблемы

#### 1. "Token is invalid"
- Проверьте правильность токена в файле `.env`
- Убедитесь, что токен не содержит лишних символов

#### 2. "Module not found"
- Активируйте виртуальное окружение
- Переустановите зависимости: `pip install -r requirements.txt`

#### 3. "Permission denied"
- Проверьте права доступа к файлам
- Убедитесь, что у процесса есть права на запись

#### 4. "Database error"
- Проверьте права на запись в директорию
- Убедитесь, что SQLite доступен

### Отладка

```bash
# Запуск с отладочным режимом
DEBUG=True python3 bot.py

# Проверка синтаксиса
python3 -m py_compile bot.py

# Проверка импортов
python3 -c "import bot; print('OK')"
```

## 📊 Мониторинг

### Проверка состояния бота

```bash
# Проверка процесса
ps aux | grep bot.py

# Проверка логов
tail -f bot.log

# Проверка базы данных
sqlite3 game_database.db ".tables"
```

### Метрики

Бот автоматически ведет статистику:
- Количество игр
- Количество дуэлей
- Активные пользователи
- Ошибки

## 🔒 Безопасность

### Рекомендации

1. **Токен бота**: Никогда не публикуйте токен в открытом доступе
2. **Файл .env**: Добавьте `.env` в `.gitignore`
3. **Права доступа**: Ограничьте доступ к файлам бота
4. **Логи**: Не логируйте чувствительную информацию
5. **Обновления**: Регулярно обновляйте зависимости

### Проверка безопасности

```bash
# Проверка зависимостей
pip-audit

# Проверка синтаксиса
python3 -m py_compile *.py

# Проверка стиля кода
pip install flake8
flake8 *.py
```

## 📞 Поддержка

Если у вас возникли проблемы:

1. Проверьте раздел "Устранение неполадок"
2. Просмотрите логи: `tail -f bot.log`
3. Запустите тесты: `python3 test_import.py`
4. Создайте Issue в репозитории

## 🎯 Следующие шаги

После успешной установки:

1. Протестируйте бота в Telegram
2. Настройте мониторинг
3. Настройте автоматические бэкапы
4. Рассмотрите возможность развертывания в облаке

---

**Удачной игры! 🍀**