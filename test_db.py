import os
import time
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Загружаем настройки из .env
load_dotenv()

# Формируем строку подключения
user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
db = os.getenv("POSTGRES_DB")
host = "localhost"
port = "5432"

DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{db}"

print(f"🔌 Пробуем подключиться к: postgresql://{user}:***@{host}:{port}/{db}")

try:
    # Создаем движок
    engine = create_engine(DATABASE_URL)
    
    # Пробуем выполнить простейший запрос
    with engine.connect() as connection:
        result = connection.execute(text("SELECT version();"))
        version = result.fetchone()[0]
        print("\n✅ УСПЕХ! Соединение установлено.")
        print(f"🐘 Версия базы: {version}")

except Exception as e:
    print("\n❌ Ошибка подключения:")
    print(e)