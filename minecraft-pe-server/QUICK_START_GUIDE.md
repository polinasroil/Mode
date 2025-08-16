# 🚀 Быстрый старт Minecraft PE Server

## ⚡ Самый быстрый способ запуска

### 1. Клонирование и переход
```bash
git clone https://github.com/your-username/minecraft-pe-server.git
cd minecraft-pe-server
```

### 2. Быстрый запуск (рекомендуется для тестирования)
```bash
python3 quick_start.py
```

**Готово!** 🎉 Сервер запущен и доступен по адресам:
- **Minecraft PE**: `localhost:19132`
- **Веб-панель**: `http://localhost:8080`
- **Логин**: `admin` / **Пароль**: `admin123`

---

## 🔧 Полная установка (для продакшена)

### 1. Установка зависимостей
```bash
pip3 install -r requirements.txt
```

### 2. Запуск скрипта установки
```bash
chmod +x scripts/install.sh
./scripts/install.sh
```

### 3. Запуск сервера
```bash
./scripts/start.sh
```

---

## 📱 Подключение с Minecraft PE

1. Откройте Minecraft PE на телефоне
2. Нажмите "Играть" → "Серверы"
3. Нажмите "Добавить сервер"
4. Введите:
   - **Название**: `Minecraft PE Server`
   - **IP адрес**: `localhost` (или IP вашего компьютера)
   - **Порт**: `19132`
5. Нажмите "Сохранить" и подключитесь

---

## 🌐 Веб-панель управления

### Доступ
- **URL**: `http://localhost:8080`
- **Логин**: `admin`
- **Пароль**: `admin123`

### Основные функции
- 📊 **Панель управления** - Обзор сервера
- 👥 **Игроки** - Управление игроками
- 🌍 **Миры** - Настройка миров
- 🔌 **Плагины** - Управление плагинами
- 💻 **Консоль** - Команды сервера
- ⚙️ **Настройки** - Конфигурация
- 💾 **Резервные копии** - Управление бэкапами

---

## 🛠️ Управление сервером

### Основные команды
```bash
./scripts/start.sh      # Запуск
./scripts/stop.sh       # Остановка
./scripts/restart.sh    # Перезапуск
./scripts/status.sh     # Статус
./scripts/update.sh     # Обновление
```

### Systemd (Linux)
```bash
sudo systemctl start minecraft-pe-server
sudo systemctl stop minecraft-pe-server
sudo systemctl status minecraft-pe-server
sudo systemctl enable minecraft-pe-server
```

---

## 🔧 Настройка

### Основные настройки сервера
```properties
# config/server.properties
server-name=Мой Minecraft Сервер
server-port=19132
max-players=20
gamemode=survival
difficulty=normal
```

### Настройки веб-панели
```properties
# config/web-panel.properties
web-port=8080
admin-username=admin
admin-password=мой_пароль
theme=dark
language=ru
```

---

## 🧪 Тестирование

### Запуск тестов
```bash
# Все тесты
python3 tests/run_tests.py

# Список тестов
python3 tests/run_tests.py list

# Тесты с покрытием
python3 tests/run_tests.py coverage
```

---

## 🐛 Устранение неполадок

### Сервер не запускается
```bash
# Проверка портов
netstat -tuln | grep :19132
netstat -tuln | grep :8080

# Проверка логов
tail -f logs/server.log
```

### Веб-панель недоступна
```bash
# Проверка процесса
ps aux | grep python

# Проверка порта
curl http://localhost:8080
```

### Игроки не могут подключиться
- Проверьте файрвол
- Убедитесь, что порт 19132 открыт
- Проверьте IP адрес сервера

---

## 📚 Дополнительная документация

- **README.md** - Полная документация проекта
- **CONTRIBUTING.md** - Руководство по вкладу
- **PROJECT_INFO.md** - Подробная информация о проекте

---

## 🆘 Получение помощи

- **GitHub Issues**: Создайте issue для сообщения об ошибках
- **Discord**: Присоединитесь к серверу сообщества
- **Email**: support@minecraft-pe-server.com

---

## 🎯 Следующие шаги

1. **Настройте конфигурацию** под ваши нужды
2. **Добавьте плагины** для расширения функциональности
3. **Настройте резервное копирование** для безопасности
4. **Присоединитесь к сообществу** для получения поддержки
5. **Внесите вклад** в развитие проекта

---

**🎉 Поздравляем! Ваш Minecraft PE Server успешно запущен и готов к использованию!**

Если у вас есть вопросы или нужна помощь, не стесняйтесь обращаться к сообществу.