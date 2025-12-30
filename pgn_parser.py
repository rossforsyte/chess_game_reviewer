import io
import chess.pgn
from datetime import datetime
from models import Game

class PGNParser:
    @staticmethod
    def parse_game(pgn_text, source_site):
        """
        Превращает PGN-текст в объект Game для базы данных.
        """
        # Читаем PGN из строки
        pgn_io = io.StringIO(pgn_text)
        game = chess.pgn.read_game(pgn_io)
        
        headers = game.headers
        
        # 1. Работаем с датой
        date_str = headers.get("Date", "")
        game_date = None
        try:
            if date_str and "?" not in date_str:
                game_date = datetime.strptime(date_str, "%Y.%m.%d")
        except ValueError:
            pass 

        # 2. Формируем уникальный ID
        # Chess.com дает ссылку в поле Link, Lichess в Site
        site_url = headers.get("Link", "") or headers.get("Site", "")
        # Если ссылка есть, берем её как ID, иначе генерируем из заголовков (редкий случай)
        site_game_id = site_url if site_url else f"{source_site}_{date_str}_{headers.get('White')}"
        
        # 3. Рейтинги
        try:
            w_elo = int(headers.get("WhiteElo", 0))
            b_elo = int(headers.get("BlackElo", 0))
        except ValueError:
            w_elo, b_elo = 0, 0

        # 4. Собираем объект
        return Game(
            site=source_site,
            site_game_id=site_game_id,
            white_player=headers.get("White", "Unknown"),
            black_player=headers.get("Black", "Unknown"),
            white_elo=w_elo,
            black_elo=b_elo,
            result=headers.get("Result", "*"),
            time_control=headers.get("TimeControl", ""),
            eco=headers.get("ECO", ""),
            opening_name=headers.get("Opening", ""),
            date_played=game_date,
            pgn_text=pgn_text,
            is_analyzed=False,
            meta={} # Пустой JSON для будущих данных
        )