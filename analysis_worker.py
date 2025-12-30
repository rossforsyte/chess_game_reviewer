import json
import chess.pgn
import io
import math
from stockfish import Stockfish
from sqlalchemy.orm import Session
from database import SessionLocal
from config import settings
from models import Game, Move

class AnalysisWorker:
    def __init__(self):
        print("⚙️ Инициализация движка Stockfish...")
        self.engine = Stockfish(
            path=settings.STOCKFISH_PATH,
            depth=18,
            parameters={"Threads": 2, "Hash": 2048, "Minimum Thinking Time": 50}
        )

    def get_piece_value(self, piece_type):
        """Возвращает ценность фигуры в пешках"""
        values = {
            chess.PAWN: 1,
            chess.KNIGHT: 3,
            chess.BISHOP: 3,
            chess.ROOK: 5,
            chess.QUEEN: 9,
            chess.KING: 0 # Короля не оцениваем как материал
        }
        return values.get(piece_type, 0)

    def is_brilliant_move(self, board, move, best_move_str, is_best_move):
        """
        Логика Бриллианта:
        1. Это Лучший ход.
        2. Мы не бьем фигуру (это не размен).
        3. Мы ставим свою ценную фигуру под бой более дешевой фигуры (жертва).
        """
        if not is_best_move:
            return False
            
        # Если мы сами кого-то рубим - это редко бывает "бриллиантовой жертвой" 
        # (хотя бывает, но для простоты опустим)
        if board.is_capture(move):
            return False

        # Какую фигуру мы двигаем?
        piece = board.piece_at(move.from_square)
        if not piece: return False
        
        my_value = self.get_piece_value(piece.piece_type)
        
        # Кто атакует клетку, куда мы пришли?
        attackers = board.attackers(not board.turn, move.to_square)
        
        # Если нас никто не атакует - это не жертва
        if not attackers:
            return False
            
        # Проверяем, есть ли среди атакующих фигура дешевле нашей (или равная)
        # Например: Ходим Ферзем (9), а бьет Пешка (1) -> ЖЕРТВА!
        is_sacrifice = False
        for square in attackers:
            attacker_piece = board.piece_at(square)
            attacker_value = self.get_piece_value(attacker_piece.piece_type)
            
            if attacker_value < my_value:
                is_sacrifice = True
                break
        
        return is_sacrifice

    def calculate_accuracy(self, moves_data):
        if not moves_data: return 0.0
        cpls = [m['cpl'] for m in moves_data if m['cpl'] is not None and m['cpl'] < 2000]
        if not cpls: return 100.0
        avg_cpl = sum(cpls) / len(cpls)
        accuracy = 100 * math.exp(-0.00003 * avg_cpl * avg_cpl - 0.005 * avg_cpl)
        return round(max(0, min(100, accuracy)), 2)

    def get_move_category(self, cpl, is_brilliant):
        """Теперь категория зависит и от флага Бриллиант"""
        if is_brilliant: return "Brilliant" # 💎
        
        if cpl is None: return "Book"
        if cpl <= 10: return "Best"
        if cpl <= 25: return "Excellent"
        if cpl <= 50: return "Good"
        if cpl <= 100: return "Inaccuracy"
        if cpl <= 300: return "Mistake"
        return "Blunder"

    def analyze_game(self, game: Game, db: Session):
        print(f"♟️ Анализируем партию ID {game.id} ({game.white_player} vs {game.black_player})...")
        
        pgn_io = io.StringIO(game.pgn_text)
        parsed_game = chess.pgn.read_game(pgn_io)
        board = parsed_game.board()
        self.engine.set_position([])
        
        prev_eval = 0.3 
        white_moves_data = []
        black_moves_data = []
        
        for move in parsed_game.mainline_moves():
            is_white = board.turn
            
            # --- STOCKFISH ---
            # Передаем текущие ходы движку
            moves_history = [m.uci() for m in board.move_stack]
            self.engine.set_position(moves_history)
            
            evaluation = self.engine.get_evaluation()
            best_move_engine = self.engine.get_best_move() # Лучший ход по мнению движка
            
            # --- EVALUATION ---
            current_eval = 0
            mate_score = None
            if evaluation['type'] == 'mate':
                mate_score = evaluation['value']
                current_eval = 2000 if mate_score > 0 else -2000
            else:
                current_eval = evaluation['value'] / 100.0
            
            # --- CPL CALCULATION ---
            if is_white:
                diff = prev_eval - current_eval
            else:
                diff = current_eval - prev_eval
            
            cpl = max(0, int(diff * 100)) if mate_score is None else None
            
            # --- BRILLIANT CHECK ---
            # Проверяем на бриллиант ПЕРЕД тем, как сделать ход на доске (board.push)
            # Нам нужно знать, является ли этот ход лучшим
            is_best = (move.uci() == best_move_engine)
            
            # Но чтобы проверить жертву (под бой), нам нужно оценить позицию 
            # куда мы идем. Передаем board в состоянии "до хода"
            is_brilliant = self.is_brilliant_move(board, move, best_move_engine, is_best)
            
            # --- CATEGORY ---
            category = self.get_move_category(cpl, is_brilliant)

            # Сохраняем
            db_move = Move(
                game_id=game.id,
                move_number=board.fullmove_number,
                ply=board.ply(),
                color='w' if is_white else 'b',
                san=board.san(move),
                fen=board.fen(),
                score=current_eval,
                mate_score=mate_score,
                best_move=best_move_engine,
                centipawn_loss=cpl,
                move_category=category
            )
            db.add(db_move)
            
            move_data = {'cpl': cpl}
            if is_white: white_moves_data.append(move_data)
            else: black_moves_data.append(move_data)

            # Делаем ход на виртуальной доске
            prev_eval = current_eval
            board.push(move)

        # Финализация
        game.white_accuracy = self.calculate_accuracy(white_moves_data)
        game.black_accuracy = self.calculate_accuracy(black_moves_data)
        game.is_analyzed = True
        
        db.commit()
        print(f"✅ Готово! White Acc: {game.white_accuracy}%, Black Acc: {game.black_accuracy}%")

    def run(self):
        db = SessionLocal()
        try:
            while True:
                game = db.query(Game).filter(Game.is_analyzed == False).first()
                if not game:
                    print("💤 Все партии проанализированы!")
                    break
                try:
                    self.analyze_game(game, db)
                except Exception as e:
                    print(f"❌ Ошибка: {e}")
                    game.is_analyzed = True 
                    db.commit()
        finally:
            db.close()

if __name__ == "__main__":
    worker = AnalysisWorker()
    worker.run()