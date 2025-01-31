# Используем Python 3.10 в минимальном образе
FROM python:3.10-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем requirements.txt из backend/
COPY backend/requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код приложения из backend/app/
COPY backend/app/ ./app/

# Если brands.txt лежит в backend/app/assets/, убедимся, что он тоже скопирован
COPY backend/app/assets/ ./app/assets/

# Открываем порт 8000 (если нужно для локального тестирования)
EXPOSE 8000

# Запуск Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
