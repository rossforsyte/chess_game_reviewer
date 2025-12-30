import os
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

class Config:
    # База данных
    DATABASE_URL = os.getenv("DATABASE_URL")

    # Настройки API
    CONTACT_EMAIL = os.getenv("CONTACT_EMAIL", "unknown_user@example.com")
    
    # Заголовки для HTTP-запросов (Chess.com требует User-Agent)
    HEADERS = {
        'User-Agent': f'ChessAnalyzerPro ({CONTACT_EMAIL})'
    }

    # Настройки загрузки (если в .env нет, берем дефолт)
    ARCHIVES_LIMIT = int(os.getenv("DEFAULT_ARCHIVES_LIMIT", 1))
    LICHESS_MAX_GAMES = int(os.getenv("DEFAULT_LICHESS_GAMES", 10))


    # Игрок, которого анализируем
    TARGET_USERNAME = os.getenv("TARGET_USERNAME", "Hikaru") # Если забыл в .env, будет Hikaru
    TARGET_SOURCE = os.getenv("TARGET_SOURCE", "chess_com")
    STOCKFISH_PATH = os.getenv("STOCKFISH_PATH")

# Создаем экземпляр конфига, чтобы импортировать его в другие файлы
settings = Config()