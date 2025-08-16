/**
 * Minecraft PE Server - Основной JavaScript файл
 * Автор: Minecraft PE Server Team
 * Версия: 1.0.0
 */

// Глобальные переменные
let serverStatus = false;
let updateInterval = null;

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    console.log('Minecraft PE Server - Веб-панель загружена');
    
    // Инициализация компонентов
    initTooltips();
    initModals();
    initTables();
    initForms();
    
    // Запуск автообновления
    startAutoUpdate();
    
    // Обработчики событий
    setupEventListeners();
});

/**
 * Инициализация всплывающих подсказок
 */
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Инициализация модальных окон
 */
function initModals() {
    const modalTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="modal"]'));
    modalTriggerList.map(function (modalTriggerEl) {
        return new bootstrap.Modal(modalTriggerEl);
    });
}

/**
 * Инициализация таблиц
 */
function initTables() {
    // Добавление сортировки для таблиц
    const tables = document.querySelectorAll('.table-sortable');
    tables.forEach(table => {
        const headers = table.querySelectorAll('th[data-sort]');
        headers.forEach(header => {
            header.addEventListener('click', () => {
                sortTable(table, header.dataset.sort);
            });
        });
    });
}

/**
 * Инициализация форм
 */
function initForms() {
    // Валидация форм
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
}

/**
 * Настройка обработчиков событий
 */
function setupEventListeners() {
    // Обработчик для кнопок управления сервером
    setupServerControls();
    
    // Обработчик для форм
    setupFormHandlers();
    
    // Обработчик для модальных окон
    setupModalHandlers();
    
    // Обработчик для таблиц
    setupTableHandlers();
}

/**
 * Настройка кнопок управления сервером
 */
function setupServerControls() {
    const startBtn = document.getElementById('startServer');
    const stopBtn = document.getElementById('stopServer');
    const restartBtn = document.getElementById('restartServer');
    
    if (startBtn) {
        startBtn.addEventListener('click', startServer);
    }
    
    if (stopBtn) {
        stopBtn.addEventListener('click', stopServer);
    }
    
    if (restartBtn) {
        restartBtn.addEventListener('click', restartServer);
    }
}

/**
 * Настройка обработчиков форм
 */
function setupFormHandlers() {
    // Обработчик для форм с AJAX
    const ajaxForms = document.querySelectorAll('form[data-ajax]');
    ajaxForms.forEach(form => {
        form.addEventListener('submit', handleAjaxForm);
    });
}

/**
 * Настройка обработчиков модальных окон
 */
function setupModalHandlers() {
    // Обработчик для модальных окон
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        modal.addEventListener('show.bs.modal', function(event) {
            const button = event.relatedTarget;
            const modal = this;
            
            // Загрузка данных в модальное окно
            if (button.dataset.load) {
                loadModalData(modal, button.dataset.load);
            }
        });
    });
}

/**
 * Настройка обработчиков таблиц
 */
function setupTableHandlers() {
    // Обработчик для строк таблиц
    const tableRows = document.querySelectorAll('.table tbody tr');
    tableRows.forEach(row => {
        row.addEventListener('click', function() {
            // Выделение строки
            this.classList.toggle('table-active');
        });
    });
}

/**
 * Запуск сервера
 */
async function startServer() {
    if (!confirm('Запустить сервер?')) {
        return;
    }
    
    try {
        showLoading('startServer');
        
        const response = await fetch('/api/server/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('Сервер успешно запущен', 'success');
            setTimeout(() => location.reload(), 1000);
        } else {
            showNotification('Ошибка запуска сервера: ' + data.message, 'error');
        }
    } catch (error) {
        console.error('Ошибка запуска сервера:', error);
        showNotification('Ошибка запуска сервера', 'error');
    } finally {
        hideLoading('startServer');
    }
}

/**
 * Остановка сервера
 */
async function stopServer() {
    if (!confirm('Остановить сервер?')) {
        return;
    }
    
    try {
        showLoading('stopServer');
        
        const response = await fetch('/api/server/stop', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('Сервер успешно остановлен', 'success');
            setTimeout(() => location.reload(), 1000);
        } else {
            showNotification('Ошибка остановки сервера: ' + data.message, 'error');
        }
    } catch (error) {
        console.error('Ошибка остановки сервера:', error);
        showNotification('Ошибка остановки сервера', 'error');
    } finally {
        hideLoading('stopServer');
    }
}

/**
 * Перезапуск сервера
 */
async function restartServer() {
    if (!confirm('Перезапустить сервер?')) {
        return;
    }
    
    try {
        showLoading('restartServer');
        
        const response = await fetch('/api/server/restart', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('Сервер успешно перезапущен', 'success');
            setTimeout(() => location.reload(), 1000);
        } else {
            showNotification('Ошибка перезапуска сервера: ' + data.message, 'error');
        }
    } catch (error) {
        console.error('Ошибка перезапуска сервера:', error);
        showNotification('Ошибка перезапуска сервера', 'error');
    } finally {
        hideLoading('restartServer');
    }
}

/**
 * Обработка AJAX форм
 */
async function handleAjaxForm(event) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    const submitBtn = form.querySelector('button[type="submit"]');
    
    try {
        showLoading(submitBtn);
        
        const response = await fetch(form.action, {
            method: form.method,
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification(data.message || 'Операция выполнена успешно', 'success');
            
            // Закрытие модального окна если есть
            const modal = form.closest('.modal');
            if (modal) {
                const modalInstance = bootstrap.Modal.getInstance(modal);
                if (modalInstance) {
                    modalInstance.hide();
                }
            }
            
            // Обновление страницы если нужно
            if (data.reload) {
                setTimeout(() => location.reload(), 1000);
            }
        } else {
            showNotification(data.message || 'Ошибка выполнения операции', 'error');
        }
    } catch (error) {
        console.error('Ошибка отправки формы:', error);
        showNotification('Ошибка отправки формы', 'error');
    } finally {
        hideLoading(submitBtn);
    }
}

/**
 * Загрузка данных в модальное окно
 */
async function loadModalData(modal, endpoint) {
    try {
        const response = await fetch(endpoint);
        const data = await response.json();
        
        if (data.success) {
            // Заполнение полей модального окна
            Object.keys(data.data).forEach(key => {
                const field = modal.querySelector(`[name="${key}"]`);
                if (field) {
                    field.value = data.data[key];
                }
            });
        }
    } catch (error) {
        console.error('Ошибка загрузки данных:', error);
    }
}

/**
 * Сортировка таблицы
 */
function sortTable(table, column) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    const header = table.querySelector(`th[data-sort="${column}"]`);
    
    // Определение направления сортировки
    const isAscending = !header.classList.contains('sort-desc');
    
    // Сортировка строк
    rows.sort((a, b) => {
        const aValue = a.querySelector(`td[data-${column}]`).textContent;
        const bValue = b.querySelector(`td[data-${column}]`).textContent;
        
        if (isAscending) {
            return aValue.localeCompare(bValue);
        } else {
            return bValue.localeCompare(aValue);
        }
    });
    
    // Обновление таблицы
    rows.forEach(row => tbody.appendChild(row));
    
    // Обновление заголовка
    table.querySelectorAll('th[data-sort]').forEach(th => {
        th.classList.remove('sort-asc', 'sort-desc');
    });
    
    header.classList.add(isAscending ? 'sort-asc' : 'sort-desc');
}

/**
 * Показать уведомление
 */
function showNotification(message, type = 'info') {
    const alertClass = `alert-${type}`;
    const iconClass = getIconClass(type);
    
    const alert = document.createElement('div');
    alert.className = `alert ${alertClass} alert-dismissible fade show`;
    alert.innerHTML = `
        <i class="${iconClass} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Добавление уведомления на страницу
    const container = document.querySelector('.container-fluid') || document.querySelector('.container');
    container.insertBefore(alert, container.firstChild);
    
    // Автоматическое удаление через 5 секунд
    setTimeout(() => {
        if (alert.parentNode) {
            alert.remove();
        }
    }, 5000);
}

/**
 * Получить класс иконки для типа уведомления
 */
function getIconClass(type) {
    const icons = {
        'success': 'fas fa-check-circle',
        'error': 'fas fa-exclamation-circle',
        'warning': 'fas fa-exclamation-triangle',
        'info': 'fas fa-info-circle'
    };
    
    return icons[type] || icons.info;
}

/**
 * Показать индикатор загрузки
 */
function showLoading(element) {
    if (typeof element === 'string') {
        element = document.getElementById(element);
    }
    
    if (element) {
        element.disabled = true;
        element.innerHTML = '<span class="loading me-2"></span>Загрузка...';
    }
}

/**
 * Скрыть индикатор загрузки
 */
function hideLoading(element) {
    if (typeof element === 'string') {
        element = document.getElementById(element);
    }
    
    if (element) {
        element.disabled = false;
        element.innerHTML = element.dataset.originalText || element.innerHTML;
    }
}

/**
 * Запуск автообновления
 */
function startAutoUpdate() {
    // Обновление статуса сервера каждые 30 секунд
    updateInterval = setInterval(async () => {
        try {
            const response = await fetch('/api/server/status');
            const data = await response.json();
            
            if (data.success !== undefined) {
                updateServerStatus(data);
            }
        } catch (error) {
            console.error('Ошибка обновления статуса:', error);
        }
    }, 30000);
}

/**
 * Обновление статуса сервера
 */
function updateServerStatus(data) {
    // Обновление индикаторов статуса
    const statusElements = document.querySelectorAll('.server-status');
    statusElements.forEach(element => {
        if (data.running) {
            element.classList.remove('text-danger');
            element.classList.add('text-success');
            element.textContent = 'Запущен';
        } else {
            element.classList.remove('text-success');
            element.classList.add('text-danger');
            element.textContent = 'Остановлен';
        }
    });
    
    // Обновление счетчиков игроков
    const playerCountElements = document.querySelectorAll('.player-count');
    playerCountElements.forEach(element => {
        element.textContent = data.players_online || 0;
    });
    
    // Обновление времени работы
    const uptimeElements = document.querySelectorAll('.server-uptime');
    uptimeElements.forEach(element => {
        element.textContent = data.uptime || '0s';
    });
}

/**
 * Форматирование размера файла
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Форматирование времени
 */
function formatTime(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
        return `${hours}h ${minutes}m ${secs}s`;
    } else if (minutes > 0) {
        return `${minutes}m ${secs}s`;
    } else {
        return `${secs}s`;
    }
}

/**
 * Экспорт данных в CSV
 */
function exportToCSV(data, filename) {
    const csvContent = "data:text/csv;charset=utf-8," + data;
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", filename);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

/**
 * Экспорт данных в JSON
 */
function exportToJSON(data, filename) {
    const jsonContent = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(data, null, 2));
    const link = document.createElement("a");
    link.setAttribute("href", jsonContent);
    link.setAttribute("download", filename);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

/**
 * Копирование в буфер обмена
 */
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showNotification('Скопировано в буфер обмена', 'success');
    } catch (error) {
        console.error('Ошибка копирования:', error);
        showNotification('Ошибка копирования', 'error');
    }
}

/**
 * Очистка при выгрузке страницы
 */
window.addEventListener('beforeunload', function() {
    if (updateInterval) {
        clearInterval(updateInterval);
    }
});

// Экспорт функций для использования в других модулях
window.MinecraftPEServer = {
    startServer,
    stopServer,
    restartServer,
    showNotification,
    formatFileSize,
    formatTime,
    exportToCSV,
    exportToJSON,
    copyToClipboard
};