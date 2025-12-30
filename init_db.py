from database import engine, Base
# Импортируем обе модели!
from models import Game, Move 

def init_db():
    print("🗑️ Удаляем старые таблицы (если есть)...")
    Base.metadata.drop_all(bind=engine) # Внимание! Это удалит все данные. Сейчас это ок.
    
    print("🐘 Создаем новую структуру базы данных...")
    Base.metadata.create_all(bind=engine)
    print("✅ Таблицы Games и Moves успешно созданы!")

if __name__ == "__main__":
    init_db()