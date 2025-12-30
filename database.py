from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings

# Создаем движок (Engine) - это сердце подключения
# echo=False отключает вывод каждого SQL-запроса в консоль (иначе будет спам)
engine = create_engine(settings.DATABASE_URL, echo=False)

# Фабрика сессий. Сессия — это "транзакция" или "ручка", которой мы пишем в базу
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для всех наших моделей
Base = declarative_base()

# Функция для получения сессии (понадобится позже для API)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()