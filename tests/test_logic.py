import sys
import os
# Добавляем корневую папку в путь, чтобы видеть модули
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pgn_parser import PGNParser

def test_pgn_parsing():
    # Имитируем PGN-текст
    fake_pgn = """
[Event "Live Chess"]
[Site "Chess.com"]
[Date "2023.10.01"]
[White "Hero"]
[Black "Villain"]
[Result "1-0"]
[WhiteElo "1500"]
[BlackElo "1450"]

1. e4 e5 2. Nf3 Nc6 1-0
    """
    
    game = PGNParser.parse_game(fake_pgn, "chess_com")
    
    assert game.white_player == "Hero"
    assert game.black_player == "Villain"
    assert game.white_elo == 1500
    assert game.result == "1-0"
    print("✅ Тест парсера пройден!")