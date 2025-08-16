#!/bin/bash

# Скрипт для создания .mcaddon файла для Minecraft PE
# Ore Collector Mod

echo "Создание .mcaddon файла для Ore Collector Mod..."

# Создаем временную папку для мода
MOD_NAME="ore_collector_mod"
TEMP_DIR="./temp_${MOD_NAME}"

# Очищаем предыдущие временные файлы
if [ -d "$TEMP_DIR" ]; then
    rm -rf "$TEMP_DIR"
fi

# Создаем структуру папок
mkdir -p "$TEMP_DIR/behavior_pack"
mkdir -p "$TEMP_DIR/resource_pack"

# Копируем файлы behavior pack
echo "Копирование файлов behavior pack..."
cp -r behavior_pack/* "$TEMP_DIR/behavior_pack/"

# Копируем файлы resource pack
echo "Копирование файлов resource pack..."
cp -r resource_pack/* "$TEMP_DIR/resource_pack/"

# Создаем ZIP архив
echo "Создание ZIP архива..."
cd "$TEMP_DIR"
zip -r "../${MOD_NAME}.zip" . > /dev/null 2>&1
cd ..

# Переименовываем в .mcaddon
echo "Переименование в .mcaddon..."
mv "${MOD_NAME}.zip" "${MOD_NAME}.mcaddon"

# Очищаем временные файлы
rm -rf "$TEMP_DIR"

echo "Готово! Создан файл: ${MOD_NAME}.mcaddon"
echo ""
echo "Теперь вы можете:"
echo "1. Скопировать ${MOD_NAME}.mcaddon на ваш телефон"
echo "2. Открыть файл в Minecraft PE"
echo "3. Импортировать мод в мир"
echo ""
echo "Не забудьте активировать оба пака в настройках мира!"