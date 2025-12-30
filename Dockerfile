# Используем легкий Linux образ с Python
FROM python:3.11-slim

# 1. Устанавливаем системные зависимости
# git нужен для скачивания, stockfish устанавливаем из репозитория Linux (это проще, чем качать бинарник вручную)
RUN apt-get update && apt-get install -y \
    stockfish \
    git \
    && rm -rf /var/lib/apt/lists/*

# 2. Создаем рабочую директорию
WORKDIR /app

# 3. Копируем зависимости и ставим их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Копируем весь код
COPY . .

# 5. Указываем переменную окружения для Stockfish
# В Linux (Debian/Ubuntu) stockfish ставится сюда:
ENV STOCKFISH_PATH=/usr/games/stockfish

# Команда по умолчанию (можно переопределить при запуске)
CMD ["python", "main_loader.py"]