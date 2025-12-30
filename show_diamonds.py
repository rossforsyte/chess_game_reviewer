import chess
from sqlalchemy import or_, and_
from database import SessionLocal
from models import Game, Move
from config import settings

def show_diamonds_terminal():
    session = SessionLocal()
    me = settings.TARGET_USERNAME
    
    # Ищем бриллианты
    brilliants = session.query(Move).join(Game).filter(
        Move.move_category == 'Brilliant',
        or_(
            and_(Game.white_player.ilike(me), Move.color == 'w'),
            and_(Game.black_player.ilike(me), Move.color == 'b')
        )
    ).order_by(Game.date_played.desc()).all()

    if not brilliants:
        print("💎 Бриллиантов пока нет. Возможно, анализ еще идет?")
        return

    print(f"\n💎 НАЙДЕНО БРИЛЛИАНТОВ: {len(brilliants)}")
    print("="*50)

    for i, move in enumerate(brilliants, 1):
        game = move.game
        opponent = game.black_player if game.white_player.lower() == me.lower() else game.white_player
        
        print(f"\n[{i}] 📅 {game.date_played.date()} | vs {opponent} | Ход: {move.move_number}. {move.san}")
        print(f"   ID Партии: {game.id}")
        print("-" * 30)
        
        # Воссоздаем доску из FEN (позиция ПЕРЕД ходом)
        board = chess.Board(move.fen)
        
        # Печатаем доску в консоль (Юникод фигуры)
        print(board.unicode(invert_color=True, borders=True))
        
        print(f"\n🚀 ТВОЙ ХОД: {move.san} (Бриллиант!)")
        print("="*50)

if __name__ == "__main__":
    show_diamonds_terminal()