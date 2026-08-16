#!/usr/bin/env bash
set -euo pipefail

echo "=== [1/5] Проверка структуры распаковки ==="
if [ ! -f "project.godot" ]; then
    echo "[ОШИБКА] project.godot не найден в корне воркспейса!"
    exit 1
fi

echo "=== [2/5] Запуск валидации файлов (validate_project.py) ==="
python3 validate_project.py

echo "=== [3/5] Первый проход: предварительный импорт ресурсов через редактор ==="
godot --headless --editor --path . --quit

echo "=== [4/5] Второй проход: полный переимпорт всех ассетов ==="
godot --headless --path . --import --quit

echo "=== [5/5] Экспорт Android APK ==="
mkdir -p build/android
godot --headless --path . --export-release "Android" build/android/VoxelVerse_2.0_Integrity.apk

if [ ! -f "build/android/VoxelVerse_2.0_Integrity.apk" ]; then
    echo "[ОШИБКА] APK-файл не был создан!"
    exit 1
fi

APK_SIZE=$(stat -c%s "build/android/VoxelVerse_2.0_Integrity.apk")
echo "Размер собранного APK: $APK_SIZE байт"

if [ "$APK_SIZE" -lt 1048576 ]; then
    echo "[ОШИБКА] APK подозрительно маленький (< 1 МБ), возможна ошибка экспорта!"
    exit 1
fi

unzip -tq "build/android/VoxelVerse_2.0_Integrity.apk"
sha256sum "build/android/VoxelVerse_2.0_Integrity.apk" | tee "build/android/VoxelVerse_2.0_Integrity.apk.sha256"
echo "=== СБОРКА УСПЕШНО ЗАВЕРШЕНА ==="
