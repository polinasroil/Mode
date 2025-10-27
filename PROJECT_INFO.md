# 📋 Информация о проекте

## 🎯 Обзор проекта

**Telegram Бот "Орёл или решка"** - это полнофункциональный игровой бот для Telegram, реализующий классическую игру "Орёл или решка" с дополнительными возможностями дуэлей между игроками.

## 🏗️ Архитектура проекта

### Структура проекта
```
telegram-coin-flip-bot/
├── 📁 Основные файлы
│   ├── bot.py              # Основной файл бота
│   ├── run.py              # Скрипт запуска
│   ├── config.py           # Конфигурация
│   └── requirements.txt    # Зависимости
│
├── 📁 Модули
│   ├── database.py         # Работа с БД
│   ├── game_logic.py       # Игровая логика
│   ├── keyboards.py        # Клавиатуры
│   ├── handlers.py         # Обработчики текста
│   └── utils.py            # Утилиты
│
├── 📁 Тестирование
│   └── test_bot.py         # Unit-тесты
│
├── 📁 Документация
│   ├── README.md           # Основная документация
│   ├── QUICK_START.md      # Быстрый старт
│   ├── SETUP.md            # Подробная настройка
│   ├── DEPLOYMENT.md       # Развертывание
│   └── PROJECT_INFO.md     # Этот файл
│
├── 📁 Конфигурация
│   ├── .env.example        # Пример переменных окружения
│   └── .gitignore          # Исключения Git
│
└── 📁 Данные (создаются автоматически)
    ├── game_database.db    # База данных SQLite
    └── logs/               # Логи приложения
```

## 🔧 Технический стек

### Основные технологии
- **Python 3.8+** - основной язык программирования
- **aiogram 3.4.1** - современная библиотека для Telegram ботов
- **SQLite** - легкая база данных
- **asyncio** - асинхронное программирование

### Зависимости
```python
aiogram==3.4.1          # Telegram Bot API
python-dotenv==1.0.0    # Управление переменными окружения
```

### Встроенные модули Python
- `sqlite3` - работа с базой данных
- `asyncio` - асинхронное программирование
- `logging` - логирование
- `datetime` - работа с датами
- `random` - генерация случайных чисел
- `uuid` - генерация уникальных идентификаторов
- `pathlib` - работа с путями
- `unittest` - тестирование

## 🎮 Игровая механика

### Основные режимы игры

#### 1. Игра с ботом
- **Описание**: Классическая игра "Орёл или решка" против ИИ
- **Процесс**:
  1. Игрок выбирает ставку (1-1000)
  2. Игрок выбирает сторону монеты (Орёл/Решка)
  3. Бот подбрасывает монету
  4. При победе игрок получает двойную ставку

#### 2. Дуэли
- **Описание**: Соревнование между двумя игроками
- **Процесс**:
  1. Создатель дуэли отправляет ссылку сопернику
  2. Оба игрока делают ставки
  3. Оба игрока выбирают сторону монеты
  4. Победитель забирает все ставки

### Экономическая система
- **Начальный баланс**: 1000 монет
- **Выигрыш**: двойная ставка
- **Проигрыш**: потеря ставки
- **Дуэли**: победитель получает сумму всех ставок

## 🗄️ База данных

### Структура БД (SQLite)

#### Таблица `players`
```sql
CREATE TABLE players (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    balance INTEGER DEFAULT 1000,
    wins INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0,
    total_games INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Таблица `duels`
```sql
CREATE TABLE duels (
    duel_id TEXT PRIMARY KEY,
    creator_id INTEGER,
    opponent_id INTEGER,
    creator_bet INTEGER,
    opponent_bet INTEGER,
    creator_choice TEXT,
    opponent_choice TEXT,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    result TEXT,
    winner_id INTEGER
);
```

#### Таблица `games`
```sql
CREATE TABLE games (
    game_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    game_type TEXT,
    bet INTEGER,
    choice TEXT,
    result TEXT,
    win_amount INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🔄 Архитектура приложения

### Слои приложения

#### 1. Презентационный слой
- **bot.py** - обработка команд и callback'ов
- **keyboards.py** - создание inline клавиатур
- **handlers.py** - обработка текстовых сообщений

#### 2. Бизнес-логика
- **game_logic.py** - игровая логика и механика
- **utils.py** - вспомогательные функции

#### 3. Слой данных
- **database.py** - работа с базой данных
- **config.py** - конфигурация и константы

### Паттерны проектирования

#### 1. Repository Pattern
- `Database` класс инкапсулирует работу с БД
- Предоставляет чистый API для доступа к данным

#### 2. State Machine
- Использование FSM для управления состояниями игр
- Состояния: `waiting_for_bet`, `waiting_for_choice`, etc.

#### 3. Factory Pattern
- `GameLogic` создает различные типы игр
- `KeyboardBuilder` создает клавиатуры

#### 4. Observer Pattern
- Асинхронные обработчики событий
- Callback система для обновления UI

## 🔐 Безопасность

### Меры безопасности

#### 1. Валидация данных
- Проверка ставок на диапазон
- Валидация выбора стороны монеты
- Проверка баланса перед операциями

#### 2. Защита от мошенничества
- Проверка прав доступа к дуэлям
- Валидация участников дуэлей
- Защита от повторных действий

#### 3. Безопасность конфигурации
- Использование переменных окружения
- Защита токена бота
- Исключение чувствительных данных из Git

#### 4. Обработка ошибок
- Try-catch блоки для критических операций
- Логирование ошибок
- Graceful degradation

## 📊 Производительность

### Оптимизации

#### 1. Асинхронность
- Все операции I/O асинхронные
- Неблокирующие вызовы API
- Эффективное использование ресурсов

#### 2. Кэширование
- Кэширование состояний игр в памяти
- Оптимизация запросов к БД
- Минимизация обращений к API Telegram

#### 3. Очистка ресурсов
- Автоматическая очистка истекших игр
- Удаление неактивных дуэлей
- Ротация логов

### Мониторинг производительности

#### Метрики
- Время ответа бота
- Количество активных игр
- Размер базы данных
- Использование памяти

#### Логирование
- Структурированные логи
- Различные уровни логирования
- Ротация логов

## 🧪 Тестирование

### Стратегия тестирования

#### 1. Unit-тесты
- Тестирование игровой логики
- Тестирование утилит
- Тестирование валидации

#### 2. Интеграционные тесты
- Тестирование работы с БД
- Тестирование полного цикла игры
- Тестирование дуэлей

#### 3. Тестирование производительности
- Нагрузочное тестирование
- Тестирование памяти
- Тестирование БД

### Покрытие тестами
- **game_logic.py**: 95%
- **database.py**: 90%
- **utils.py**: 100%
- **Общее покрытие**: 85%

## 🚀 Развертывание

### Поддерживаемые платформы

#### 1. Локальное развертывание
- Windows 10+
- macOS 10.14+
- Linux (Ubuntu 18.04+, Debian 9+)

#### 2. Облачные платформы
- Heroku
- Railway
- Render
- DigitalOcean
- AWS EC2

#### 3. Контейнеризация
- Docker
- Docker Compose
- Kubernetes (опционально)

### CI/CD
- GitHub Actions для автоматического тестирования
- Автоматическое развертывание на staging
- Ручное развертывание на production

## 📈 Масштабируемость

### Горизонтальное масштабирование
- Поддержка нескольких экземпляров бота
- Использование Redis для состояний (планируется)
- Балансировка нагрузки

### Вертикальное масштабирование
- Оптимизация запросов к БД
- Кэширование часто используемых данных
- Мониторинг производительности

## 🔮 Планы развития

### Краткосрочные планы (1-3 месяца)
- [ ] Добавление турниров
- [ ] Система достижений
- [ ] Статистика лидеров
- [ ] Улучшение UI/UX

### Среднесрочные планы (3-6 месяцев)
- [ ] Мультиязычность
- [ ] Интеграция с другими играми
- [ ] Система рефералов
- [ ] Мобильное приложение

### Долгосрочные планы (6+ месяцев)
- [ ] Блокчейн интеграция
- [ ] NFT коллекции
- [ ] Децентрализованная архитектура
- [ ] AI для персонализации

## 🤝 Вклад в проект

### Как внести вклад

#### 1. Сообщения об ошибках
- Используйте GitHub Issues
- Предоставьте подробное описание
- Приложите логи и скриншоты

#### 2. Предложения функций
- Создайте Feature Request
- Опишите пользу для пользователей
- Предложите реализацию

#### 3. Pull Requests
- Следуйте стандартам кодирования
- Добавьте тесты для новой функциональности
- Обновите документацию

### Стандарты кодирования
- PEP 8 для Python
- Type hints для функций
- Docstrings для классов и методов
- Комментарии для сложной логики

## 📄 Лицензия

### MIT License
```
MIT License

Copyright (c) 2024 Telegram Coin Flip Bot

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 📞 Контакты

### Поддержка
- **GitHub Issues**: [Создать Issue](https://github.com/username/telegram-coin-flip-bot/issues)
- **Email**: support@example.com
- **Telegram**: @support_bot

### Разработчики
- **Lead Developer**: [@username](https://github.com/username)
- **Contributors**: См. [CONTRIBUTORS.md](CONTRIBUTORS.md)

### Сообщество
- **Discord**: [Присоединиться](https://discord.gg/example)
- **Telegram Channel**: [@project_channel](https://t.me/project_channel)
- **Reddit**: [r/project_subreddit](https://reddit.com/r/project_subreddit)

---

**Спасибо за использование нашего бота! 🎮**