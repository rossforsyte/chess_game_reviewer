import sys
import os
# Добавляем корневую папку в путь
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Game

def test_game_model_creation():
    # Тестируем создание объекта Game (без сохранения в БД)
    game = Game(
        site_game_id="https://www.chess.com/game/live/123456",
        white_player="Hero",
        black_player="Villain",
        white_elo=1500,
        black_elo=1400,
        result="1-0",
        pgn_text="1. e4 e5"
    )
    
    assert game.white_player == "Hero"
    assert game.result == "1-0"
    print("✅ Тест модели Game пройден!")

def test_simple_math():
    # Простейший тест, чтобы убедиться, что pytest работает
    assert 2 + 2 == 4