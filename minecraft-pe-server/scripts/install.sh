#!/bin/bash

# Minecraft PE Server - Скрипт установки
# Автор: Minecraft PE Server Team
# Версия: 1.0.0

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функции для вывода
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Проверка операционной системы
check_os() {
    print_info "Проверка операционной системы..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        print_success "Обнаружена Linux система"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        print_success "Обнаружена macOS система"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        OS="windows"
        print_success "Обнаружена Windows система (WSL)"
    else
        print_error "Неподдерживаемая операционная система: $OSTYPE"
        exit 1
    fi
}

# Проверка зависимостей
check_dependencies() {
    print_info "Проверка системных зависимостей..."
    
    # Проверка Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
        print_success "Python $PYTHON_VERSION найден"
    else
        print_error "Python 3 не найден. Установите Python 3.8+"
        exit 1
    fi
    
    # Проверка pip
    if command -v pip3 &> /dev/null; then
        print_success "pip3 найден"
    else
        print_error "pip3 не найден. Установите pip3"
        exit 1
    fi
    
    # Проверка git
    if command -v git &> /dev/null; then
        print_success "Git найден"
    else
        print_warning "Git не найден. Рекомендуется установить для обновлений"
    fi
}

# Установка Python зависимостей
install_python_deps() {
    print_info "Установка Python зависимостей..."
    
    # Создание виртуального окружения
    if [ ! -d "venv" ]; then
        print_info "Создание виртуального окружения..."
        python3 -m venv venv
    fi
    
    # Активация виртуального окружения
    source venv/bin/activate
    
    # Обновление pip
    pip install --upgrade pip
    
    # Установка зависимостей
    print_info "Установка основных зависимостей..."
    pip install -r requirements.txt
    
    print_success "Python зависимости установлены"
}

# Создание requirements.txt
create_requirements() {
    print_info "Создание файла requirements.txt..."
    
    cat > requirements.txt << EOF
# Minecraft PE Server - Python зависимости
# Автор: Minecraft PE Server Team
# Версия: 1.0.0

# Основные зависимости
Flask==2.3.3
Flask-Login==0.6.3
Werkzeug==2.3.7
psutil==5.9.5
PyYAML==6.0.1

# Дополнительные зависимости
requests==2.31.0
aiohttp==3.8.6
asyncio-mqtt==0.13.0
redis==5.0.1
sqlalchemy==2.0.21

# Зависимости для разработки
pytest==7.4.2
pytest-asyncio==0.21.1
black==23.9.1
flake8==6.1.0
mypy==1.5.1
EOF
    
    print_success "Файл requirements.txt создан"
}

# Создание структуры директорий
create_directories() {
    print_info "Создание структуры директорий..."
    
    # Основные директории
    mkdir -p logs
    mkdir -p backups
    mkdir -p worlds
    mkdir -p plugins
    mkdir -p data
    mkdir -p temp
    
    # Директории для плагинов
    mkdir -p plugins/core
    mkdir -p plugins/optional
    
    # Директории для данных
    mkdir -p data/players
    mkdir -p data/worlds
    mkdir -p data/plugins
    
    print_success "Структура директорий создана"
}

# Создание конфигурационных файлов
create_configs() {
    print_info "Создание конфигурационных файлов..."
    
    # Основной конфигурационный файл
    if [ ! -f "config/server.properties" ]; then
        print_info "Создание server.properties..."
        cp config/server.properties.example config/server.properties 2>/dev/null || true
    fi
    
    # Конфигурация веб-панели
    if [ ! -f "config/web-panel.properties" ]; then
        print_info "Создание web-panel.properties..."
        cp config/web-panel.properties.example config/web-panel.properties 2>/dev/null || true
    fi
    
    # Конфигурация плагинов
    if [ ! -f "config/plugins.yml" ]; then
        print_info "Создание plugins.yml..."
        cat > config/plugins.yml << EOF
# Minecraft PE Server - Конфигурация плагинов
# Автор: Minecraft PE Server Team
# Версия: 1.0.0

plugins:
  core:
    - name: "CoreProtect"
      enabled: true
      version: "2.0.0"
      description: "Логирование действий игроков"
    
    - name: "WorldEdit"
      enabled: true
      version: "7.2.0"
      description: "Редактирование мира"
    
    - name: "Essentials"
      enabled: true
      version: "2.19.0"
      description: "Основные команды"
    
    - name: "PermissionsEx"
      enabled: true
      version: "2.0.0"
      description: "Система прав"
  
  optional:
    - name: "WorldGuard"
      enabled: false
      version: "7.0.0"
      description: "Защита регионов"
    
    - name: "LocketteX"
      enabled: false
      version: "2.0.0"
      description: "Защита блоков"
EOF
    fi
    
    print_success "Конфигурационные файлы созданы"
}

# Создание скриптов управления
create_scripts() {
    print_info "Создание скриптов управления..."
    
    # Скрипт запуска
    cat > start.sh << 'EOF'
#!/bin/bash

# Minecraft PE Server - Скрипт запуска
# Автор: Minecraft PE Server Team
# Версия: 1.0.0

set -e

# Переход в директорию скрипта
cd "$(dirname "$0")"

# Проверка виртуального окружения
if [ ! -d "venv" ]; then
    echo "Ошибка: Виртуальное окружение не найдено. Запустите install.sh"
    exit 1
fi

# Активация виртуального окружения
source venv/bin/activate

# Проверка конфигурации
if [ ! -f "config/server.properties" ]; then
    echo "Ошибка: Конфигурация сервера не найдена"
    exit 1
fi

# Запуск сервера
echo "Запуск Minecraft PE Server..."
python3 server/main.py
EOF
    
    # Скрипт остановки
    cat > stop.sh << 'EOF'
#!/bin/bash

# Minecraft PE Server - Скрипт остановки
# Автор: Minecraft PE Server Team
# Версия: 1.0.0

# Поиск процесса сервера
SERVER_PID=$(pgrep -f "python3.*server/main.py" || true)

if [ -n "$SERVER_PID" ]; then
    echo "Остановка Minecraft PE Server (PID: $SERVER_PID)..."
    kill -TERM "$SERVER_PID"
    
    # Ожидание завершения
    sleep 5
    
    # Принудительная остановка если нужно
    if kill -0 "$SERVER_PID" 2>/dev/null; then
        echo "Принудительная остановка сервера..."
        kill -KILL "$SERVER_PID"
    fi
    
    echo "Сервер остановлен"
else
    echo "Сервер не запущен"
fi
EOF
    
    # Скрипт перезапуска
    cat > restart.sh << 'EOF'
#!/bin/bash

# Minecraft PE Server - Скрипт перезапуска
# Автор: Minecraft PE Server Team
# Версия: 1.0.0

# Переход в директорию скрипта
cd "$(dirname "$0")"

echo "Перезапуск Minecraft PE Server..."

# Остановка сервера
./stop.sh

# Ожидание
sleep 2

# Запуск сервера
./start.sh
EOF
    
    # Скрипт статуса
    cat > status.sh << 'EOF'
#!/bin/bash

# Minecraft PE Server - Скрипт проверки статуса
# Автор: Minecraft PE Server Team
# Версия: 1.0.0

# Поиск процесса сервера
SERVER_PID=$(pgrep -f "python3.*server/main.py" || true)

if [ -n "$SERVER_PID" ]; then
    echo "✅ Minecraft PE Server запущен (PID: $SERVER_PID)"
    
    # Проверка портов
    if netstat -tuln 2>/dev/null | grep -q ":19132 "; then
        echo "✅ Порт 19132 (Minecraft) активен"
    else
        echo "❌ Порт 19132 (Minecraft) не активен"
    fi
    
    if netstat -tuln 2>/dev/null | grep -q ":8080 "; then
        echo "✅ Порт 8080 (Веб-панель) активен"
    else
        echo "❌ Порт 8080 (Веб-панель) не активен"
    fi
    
    # Использование ресурсов
    if command -v ps &> /dev/null; then
        CPU=$(ps -p "$SERVER_PID" -o %cpu= 2>/dev/null || echo "N/A")
        MEM=$(ps -p "$SERVER_PID" -o %mem= 2>/dev/null || echo "N/A")
        echo "📊 Использование ресурсов: CPU: ${CPU}%, RAM: ${MEM}%"
    fi
else
    echo "❌ Minecraft PE Server не запущен"
fi
EOF
    
    # Скрипт обновления
    cat > update.sh << 'EOF'
#!/bin/bash

# Minecraft PE Server - Скрипт обновления
# Автор: Minecraft PE Server Team
# Версия: 1.0.0

set -e

# Переход в директорию скрипта
cd "$(dirname "$0")"

echo "Обновление Minecraft PE Server..."

# Остановка сервера если запущен
if pgrep -f "python3.*server/main.py" > /dev/null; then
    echo "Остановка сервера для обновления..."
    ./stop.sh
    sleep 2
fi

# Создание резервной копии
BACKUP_DIR="backups/update_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "Создание резервной копии в $BACKUP_DIR..."

# Копирование важных файлов
cp -r config "$BACKUP_DIR/"
cp -r worlds "$BACKUP_DIR/"
cp -r data "$BACKUP_DIR/"
cp -r plugins "$BACKUP_DIR/"

# Обновление кода (если используется git)
if [ -d ".git" ]; then
    echo "Обновление кода из Git..."
    git pull origin main
else
    echo "Git репозиторий не найден. Обновление кода пропущено."
fi

# Обновление зависимостей
echo "Обновление Python зависимостей..."
source venv/bin/activate
pip install --upgrade -r requirements.txt

# Восстановление конфигурации
echo "Восстановление конфигурации..."
cp -r "$BACKUP_DIR/config" ./

echo "Обновление завершено!"
echo "Резервная копия сохранена в $BACKUP_DIR"
echo "Запустите сервер командой: ./start.sh"
EOF
    
    # Делаем скрипты исполняемыми
    chmod +x start.sh stop.sh restart.sh status.sh update.sh
    
    print_success "Скрипты управления созданы"
}

# Создание systemd сервиса (для Linux)
create_systemd_service() {
    if [ "$OS" = "linux" ]; then
        print_info "Создание systemd сервиса..."
        
        SERVICE_FILE="/etc/systemd/system/minecraft-pe-server.service"
        
        if [ -w "/etc/systemd/system" ]; then
            sudo tee "$SERVICE_FILE" > /dev/null << EOF
[Unit]
Description=Minecraft PE Server
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
ExecStart=$(pwd)/start.sh
ExecStop=$(pwd)/stop.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
            
            # Перезагрузка systemd
            sudo systemctl daemon-reload
            
            print_success "Systemd сервис создан"
            print_info "Для управления сервисом используйте:"
            print_info "  sudo systemctl start minecraft-pe-server"
            print_info "  sudo systemctl stop minecraft-pe-server"
            print_info "  sudo systemctl enable minecraft-pe-server"
        else
            print_warning "Не удалось создать systemd сервис (требуются права администратора)"
        fi
    fi
}

# Создание файла .env
create_env_file() {
    print_info "Создание файла .env..."
    
    cat > .env << EOF
# Minecraft PE Server - Переменные окружения
# Автор: Minecraft PE Server Team
# Версия: 1.0.0

# Основные настройки
SERVER_NAME=Minecraft PE Server
SERVER_PORT=19132
WEB_PANEL_PORT=8080
WEB_PANEL_HOST=0.0.0.0

# База данных
DB_HOST=localhost
DB_PORT=3306
DB_NAME=minecraft_pe
DB_USER=minecraft_user
DB_PASSWORD=secure_password

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Безопасность
SECRET_KEY=your_secret_key_here
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123

# Пути
WORLDS_DIR=./worlds
PLUGINS_DIR=./plugins
BACKUPS_DIR=./backups
LOGS_DIR=./logs

# Логирование
LOG_LEVEL=INFO
LOG_FILE=./logs/server.log

# Мониторинг
ENABLE_MONITORING=true
MONITORING_INTERVAL=30
EOF
    
    print_success "Файл .env создан"
}

# Создание файла .gitignore
create_gitignore() {
    print_info "Создание файла .gitignore..."
    
    cat > .gitignore << EOF
# Minecraft PE Server - Git ignore
# Автор: Minecraft PE Server Team
# Версия: 1.0.0

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Виртуальное окружение
venv/
env/
ENV/
env.bak/
venv.bak/

# Конфигурация
.env
config/*.properties
config/*.yml
!config/*.example

# Данные
worlds/
data/
backups/
logs/
temp/

# Плагины
plugins/*.jar
plugins/*.py

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Системные файлы
.DS_Store
Thumbs.db

# Логи
*.log
*.out

# Резервные копии
*.bak
*.backup
EOF
    
    print_success "Файл .gitignore создан"
}

# Основная функция установки
main() {
    echo "🎮 Minecraft PE Server - Установка"
    echo "=================================="
    echo ""
    
    # Проверки
    check_os
    check_dependencies
    
    # Создание файлов
    create_requirements
    create_directories
    create_configs
    create_scripts
    create_env_file
    create_gitignore
    
    # Установка зависимостей
    install_python_deps
    
    # Создание systemd сервиса (для Linux)
    create_systemd_service
    
    echo ""
    echo "🎉 Установка завершена успешно!"
    echo ""
    echo "📋 Следующие шаги:"
    echo "1. Настройте конфигурацию в config/server.properties"
    echo "2. Настройте веб-панель в config/web-panel.properties"
    echo "3. Запустите сервер: ./start.sh"
    echo "4. Откройте веб-панель: http://localhost:8080"
    echo ""
    echo "🔧 Полезные команды:"
    echo "  ./start.sh     - Запуск сервера"
    echo "  ./stop.sh      - Остановка сервера"
    echo "  ./restart.sh   - Перезапуск сервера"
    echo "  ./status.sh    - Проверка статуса"
    echo "  ./update.sh    - Обновление сервера"
    echo ""
    echo "📚 Документация: README.md"
    echo "🐛 Поддержка: Создайте issue в репозитории"
}

# Запуск установки
main "$@"