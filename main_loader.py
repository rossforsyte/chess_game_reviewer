from database import SessionLocal
from game_loader import GameLoader
from pgn_parser import PGNParser
from models import Game
from config import settings
from sqlalchemy.exc import IntegrityError

def run_import(username, source="chess_com"):
    # 1. Инициализация
    db = SessionLocal()
    loader = GameLoader()
    
    print(f"🚀 Начинаем импорт партий для: {username} ({source})")
    
    # 2. Загрузка "сырых" PGN
    raw_games = []
    if source == "chess_com":
        raw_games = loader.fetch_chesscom_games(username) # Использует лимиты из config.py
    elif source == "lichess":
        raw_games = loader.fetch_lichess_games(username)
    
    if not raw_games:
        print("📭 Новых партий не найдено.")
        return

    print(f"📦 Обрабатываем {len(raw_games)} партий для сохранения в БД...")
    
    # 3. Сохранение в базу
    new_count = 0
    skip_count = 0
    
    for pgn in raw_games:
        # Парсим
        game_obj = PGNParser.parse_game(pgn, source)
        
        # Проверяем, есть ли такая партия уже в базе (по ID)
        exists = db.query(Game).filter(Game.site_game_id == game_obj.site_game_id).first()
        
        if exists:
            skip_count += 1
            continue # Пропускаем, чтобы не дублировать
            
        try:
            db.add(game_obj)
            new_count += 1
            # Можно коммитить пачками по 100 штук для скорости, 
            # но для надежности пока делаем по одной
            db.commit() 
        except IntegrityError:
            db.rollback()
            skip_count += 1
        except Exception as e:
            print(f"⚠️ Ошибка при сохранении партии: {e}")
            db.rollback()

    db.close()
    print("-" * 40)
    print(f"🏁 Импорт завершен!")
    print(f"✅ Добавлено новых: {new_count}")
    print(f"⏭️ Пропущено (дубликаты): {skip_count}")

if __name__ == "__main__":
    # Берем данные прямо из конфига
    user = settings.TARGET_USERNAME
    source = settings.TARGET_SOURCE
    
    if user == "Твой_Никнейм":
        print("⚠️  Внимание: Вы не поменяли никнейм в .env файле!")
    
    run_import(user, source=source)