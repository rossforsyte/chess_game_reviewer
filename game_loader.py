import requests
import berserk
from config import settings  # <--- Импортируем наши настройки

class GameLoader:
    def __init__(self):
        # Берем заголовки из конфига
        self.headers = settings.HEADERS
        
        # Инициализация Lichess (токен пока не нужен, но если понадобится — добавим в конфиг)
        self.session = berserk.TokenSession(None)
        self.lichess_client = berserk.Client(session=self.session)

    def fetch_chesscom_games(self, username, archives_limit=None):
        """
        Скачивает партии с Chess.com.
        Если archives_limit не передан, берет значение из конфига.
        """
        # Если аргумент не передан явно, берем из настроек
        limit = archives_limit if archives_limit is not None else settings.ARCHIVES_LIMIT
        
        print(f"📡 Подключаемся к Chess.com для пользователя {username}...")
        print(f"   (Лимит архивов: {limit} мес.)")
        
        url = f"https://api.chess.com/pub/player/{username}/games/archives"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code != 200:
                print(f"❌ Ошибка Chess.com: {response.status_code}")
                return []
            
            archives = response.json().get('archives', [])
            selected_archives = archives[-limit:]
            
            all_games = []
            for archive_url in selected_archives:
                print(f"   📥 Скачиваем архив: {archive_url}...")
                data = requests.get(archive_url, headers=self.headers, timeout=10).json()
                games = data.get('games', [])
                
                pgns = [g['pgn'] for g in games if 'pgn' in g]
                all_games.extend(pgns)
                
            print(f"✅ Успешно загружено {len(all_games)} партий с Chess.com")
            return all_games

        except Exception as e:
            print(f"❌ Критическая ошибка при загрузке с Chess.com: {e}")
            return []

    def fetch_lichess_games(self, username, max_games=None):
        """
        Скачивает партии с Lichess.
        Если max_games не передан, берет значение из конфига.
        """
        limit = max_games if max_games is not None else settings.LICHESS_MAX_GAMES
        
        print(f"🐴 Подключаемся к Lichess для пользователя {username}...")
        print(f"   (Лимит партий: {limit})")
        
        try:
            games_generator = self.lichess_client.games.export_by_player(
                username, 
                max=limit, 
                as_pgn=True
            )
            games_list = list(games_generator)
            print(f"✅ Успешно загружено {len(games_list)} партий с Lichess")
            return games_list
            
        except berserk.exceptions.ResponseError as e:
            print(f"❌ Ошибка Lichess: {e}")
            return []

# --- Тест ---
if __name__ == "__main__":
    # Теперь тут нет хардкода, всё управляется через .env или аргументы
    loader = GameLoader()
    
    # Можем проверить, что Email подтянулся
    print(f"🔧 Конфиг загружен. User-Agent: {settings.HEADERS['User-Agent']}")
    print("-" * 30)

    # Тестовый прогон (использует лимиты из .env)
    loader.fetch_chesscom_games("rogerforsyte")
    # loader.fetch_lichess_games("DrNykterstein")