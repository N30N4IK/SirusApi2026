# Используем стабильный и легковесный базовый образ Python
FROM python:3.11-slim

# Установка системных зависимостей, необходимых для работы psycopg2 (PostgreSQL)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    python3-dev \
    # Добавляем wget, чтобы было проще, если нужны скрипты ожидания
    wget \
    && rm -rf /var/lib/apt/lists/*

# Установка рабочего каталога внутри контейнера
WORKDIR /app

# Копирование файла требований и установка зависимостей
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Копирование всего исходного кода (пакет services)
# Это включает core, adapters, infrastructure, models, main.py, etc.
COPY services /app/services
COPY scripts /app/scripts

# Если скрипты находятся в project_root/scripts, их нужно скопировать
# COPY scripts /app/scripts 

# Точка входа для FastAPI. Запуск Uvicorn.
# Путь к main.py: services.infrastructure.main
CMD ["uvicorn", "services.infrastructure.main:app", "--host", "0.0.0.0", "--port", "8000"]