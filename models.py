from sqlalchemy import Column, Integer, String, Text, DateTime, Date, Float, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    
    # Уникальность: Сайт + ID партии на сайте. 
    # Если скачаем партию дважды, база не даст создать дубль.
    site = Column(String)  # 'chess.com', 'lichess'
    site_game_id = Column(String, unique=True, index=True) 
    
    # Игроки
    white_player = Column(String, index=True)
    black_player = Column(String, index=True)
    white_elo = Column(Integer)
    black_elo = Column(Integer)
    
    # Результат
    result = Column(String) # '1-0', '0-1', '1/2-1/2'
    time_control = Column(String) # '600', '180+2'
    
    # Дебют
    eco = Column(String, index=True)
    opening_name = Column(String)
    
    # Дата и текст
    date_played = Column(DateTime, index=True) # Index нужен для сортировки "мои последние партии"
    pgn_text = Column(Text)
    
    # --- Блок Аналитики (Game Review) ---
    is_analyzed = Column(Boolean, default=False, index=True) # Index нужен, чтобы быстро искать необработанные
    
    # Точность (Accuracy) - заполняем после анализа
    white_accuracy = Column(Float, nullable=True) 
    black_accuracy = Column(Float, nullable=True)
    
    # Поле для всего остального (аватарки, флаги, ссылки на турнир)
    meta = Column(JSON, nullable=True) 
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Связь
    moves = relationship("Move", back_populates="game", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Game {self.site_game_id} ({self.white_player} vs {self.black_player})>"

class Move(Base):
    __tablename__ = "moves"

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id", ondelete="CASCADE"), index=True)
    
    move_number = Column(Integer)
    ply = Column(Integer) # Полуход (1, 2, 3...)
    color = Column(String(1)) # 'w', 'b'
    
    san = Column(String(10)) 
    fen = Column(String)
    
    # Аналитика
    score = Column(Float, nullable=True) # Оценка в пешках (+1.5)
    mate_score = Column(Integer, nullable=True) # Оценка "Мат в X ходов" (если есть)
    best_move = Column(String(10), nullable=True)
    
    centipawn_loss = Column(Integer, nullable=True)
    # Brilliant, Great, Best, Excellent, Good, Inaccuracy, Mistake, Blunder, Book
    move_category = Column(String, index=True) 

    game = relationship("Game", back_populates="moves")