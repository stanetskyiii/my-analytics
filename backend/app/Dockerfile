# Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Скопируем requirements.txt
COPY requirements.txt .

# Установим зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Скопируем код
COPY app/ ./app/

# Обязательно скопируем файл brands.txt, если он лежит в app/assets
# (Но если он уже внутри app/ - этого достаточно)
# Если у нас папка app/assets, то она уже копируется командой COPY app/ ./app/
# Но на всякий случай:
# COPY app/assets/ ./app/assets/

# Запуск
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
