from sqlalchemy import or_, and_, func
from database import SessionLocal
from models import Game, Move
from config import settings

def print_simple_stats():
    session = SessionLocal()
    me = settings.TARGET_USERNAME
    
    print(f"\n📊 СТАТИСТИКА ПО МОМЕНТАМ ({me})")
    print("=" * 40)

    # 1. Считаем Бриллианты 💎
    # (Фильтр: категория = Brilliant И ход сделал ТЫ)
    brilliant_count = session.query(Move).join(Game).filter(
        Move.move_category == 'Brilliant',
        or_(
            and_(Game.white_player.ilike(me), Move.color == 'w'),
            and_(Game.black_player.ilike(me), Move.color == 'b')
        )
    ).count()

    # 2. Считаем Зевки 💀
    blunder_count = session.query(Move).join(Game).filter(
        Move.move_category == 'Blunder',
        or_(
            and_(Game.white_player.ilike(me), Move.color == 'w'),
            and_(Game.black_player.ilike(me), Move.color == 'b')
        )
    ).count()

    print(f"💎 Бриллиантовых ходов: {brilliant_count}")
    print(f"💀 Грубых ошибок (Blunders): {blunder_count}")
    print("-" * 40)

    # 3. Список партий с Бриллиантами
    if brilliant_count > 0:
        print("\n📜 ПАРТИИ С БРИЛЛИАНТАМИ:")
        
        # Получаем сами ходы
        brilliant_moves = session.query(Move).join(Game).filter(
            Move.move_category == 'Brilliant',
            or_(
                and_(Game.white_player.ilike(me), Move.color == 'w'),
                and_(Game.black_player.ilike(me), Move.color == 'b')
            )
        ).order_by(Game.date_played.desc()).all()

        for move in brilliant_moves:
            game = move.game
            # Определяем соперника
            opponent = game.black_player if game.white_player.lower() == me.lower() else game.white_player
            date_str = game.date_played.date() if game.date_played else "Неизвестная дата"
            
            print(f"🔹 {date_str} vs {opponent} | Ход {move.move_number} ({move.san})")
            # Выводим ID, чтобы можно было найти вручную, если нужно
            print(f"   ID партии в базе: {game.id}") 

    else:
        print("\n💎 Бриллиантов пока не найдено.")

    session.close()

if __name__ == "__main__":
    print_simple_stats()