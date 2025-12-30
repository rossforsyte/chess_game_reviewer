import webbrowser
import os
from sqlalchemy import or_, and_, func
from database import SessionLocal
from models import Game, Move
from config import settings

def generate_html_report():
    session = SessionLocal()
    try:
        me = settings.TARGET_USERNAME
        
        print(f"📊 Генерируем отчет для: {me}...")
        
        # 1. СТАТИСТИКА
        total_games = session.query(Game).filter(Game.is_analyzed == True).count()
        
        # Средняя точность
        avg_acc_white = session.query(func.avg(Game.white_accuracy))\
            .filter(Game.white_player.ilike(me), Game.is_analyzed == True).scalar() or 0
        avg_acc_black = session.query(func.avg(Game.black_accuracy))\
            .filter(Game.black_player.ilike(me), Game.is_analyzed == True).scalar() or 0

        # Счетчики
        brilliants_count = session.query(Move).join(Game).filter(
            Move.move_category == 'Brilliant',
            or_(
                and_(Game.white_player.ilike(me), Move.color == 'w'),
                and_(Game.black_player.ilike(me), Move.color == 'b')
            )
        ).count()

        blunders_count = session.query(Move).join(Game).filter(
            Move.move_category == 'Blunder',
            or_(
                and_(Game.white_player.ilike(me), Move.color == 'w'),
                and_(Game.black_player.ilike(me), Move.color == 'b')
            )
        ).count()

        # 2. ПОЛУЧАЕМ СПИСКИ ХОДОВ
        # Бриллианты (Топ 20 самых свежих)
        brilliant_moves = session.query(Move).join(Game).filter(
            Move.move_category == 'Brilliant',
            or_(
                and_(Game.white_player.ilike(me), Move.color == 'w'),
                and_(Game.black_player.ilike(me), Move.color == 'b')
            )
        ).order_by(Game.date_played.desc()).limit(20).all()

        # Зевки (Топ 20 самых свежих)
        blunder_moves = session.query(Move).join(Game).filter(
            Move.move_category == 'Blunder',
            or_(
                and_(Game.white_player.ilike(me), Move.color == 'w'),
                and_(Game.black_player.ilike(me), Move.color == 'b')
            )
        ).order_by(Game.date_played.desc()).limit(20).all()

        # 3. ГЕНЕРАЦИЯ HTML (ВНУТРИ СЕССИИ!)
        html_content = f"""
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <title>Chess Analyzer Pro - Отчет</title>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background: #f4f4f9; color: #333; padding: 20px; }}
                .container {{ max_width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }}
                h1 {{ text-align: center; color: #2c3e50; }}
                .stats-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 30px; }}
                .stat-card {{ background: #ecf0f1; padding: 15px; border-radius: 8px; text-align: center; }}
                .stat-value {{ font-size: 24px; font-weight: bold; color: #2980b9; }}
                .stat-label {{ font-size: 14px; color: #7f8c8d; }}
                
                h2 {{ border-bottom: 2px solid #eee; padding-bottom: 10px; margin-top: 40px; }}
                
                table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
                th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #eee; }}
                th {{ background-color: #f8f9fa; color: #7f8c8d; font-weight: 600; }}
                
                .move-brilliant {{ color: #27ae60; font-weight: bold; }}
                .move-blunder {{ color: #c0392b; font-weight: bold; }}
                
                a.btn {{ display: inline-block; padding: 6px 12px; background: #3498db; color: white; text-decoration: none; border-radius: 4px; font-size: 14px; }}
                a.btn:hover {{ background: #2980b9; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>♟️ Отчет для {me}</h1>
                
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-value">{total_games}</div>
                        <div class="stat-label">Партий в базе</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{brilliants_count} 💎</div>
                        <div class="stat-label">Бриллиантов</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{blunders_count} 💀</div>
                        <div class="stat-label">Зевков</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{avg_acc_white:.1f}% / {avg_acc_black:.1f}%</div>
                        <div class="stat-label">Точность (Белые/Черные)</div>
                    </div>
                </div>

                <h2>💎 Мои Лучшие Ходы (Brilliant)</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Дата</th>
                            <th>Соперник</th>
                            <th>Ход</th>
                            <th>Нотация</th>
                            <th>Ссылка</th>
                        </tr>
                    </thead>
                    <tbody>
        """

        for move in brilliant_moves:
            game = move.game
            opponent = game.black_player if game.white_player.lower() == me.lower() else game.white_player
            date_str = game.date_played.strftime('%Y-%m-%d') if game.date_played else "-"
            # Формируем ссылку
            link = game.site_game_id
            if "chess.com" in link:
                link += f"&move={move.ply}"
            elif "lichess" in link:
                link += f"#{move.ply}"

            html_content += f"""
                        <tr>
                            <td>{date_str}</td>
                            <td>{opponent}</td>
                            <td>{move.move_number}</td>
                            <td class="move-brilliant">{move.san}</td>
                            <td><a href="{link}" target="_blank" class="btn">Смотреть</a></td>
                        </tr>
            """

        html_content += """
                    </tbody>
                </table>

                <h2>💀 Последние Ошибки (Blunders)</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Дата</th>
                            <th>Соперник</th>
                            <th>Ход</th>
                            <th>Нотация</th>
                            <th>Потеря (CPL)</th>
                            <th>Ссылка</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        
        for move in blunder_moves:
            game = move.game
            opponent = game.black_player if game.white_player.lower() == me.lower() else game.white_player
            date_str = game.date_played.strftime('%Y-%m-%d') if game.date_played else "-"
            link = game.site_game_id
            if "chess.com" in link:
                link += f"&move={move.ply}"
            elif "lichess" in link:
                link += f"#{move.ply}"
                
            html_content += f"""
                        <tr>
                            <td>{date_str}</td>
                            <td>{opponent}</td>
                            <td>{move.move_number}</td>
                            <td class="move-blunder">{move.san}</td>
                            <td>-{move.centipawn_loss / 100:.1f} пешки</td>
                            <td><a href="{link}" target="_blank" class="btn" style="background:#e74c3c;">Разбор</a></td>
                        </tr>
            """

        html_content += """
                    </tbody>
                </table>
                
                <p style="text-align:center; margin-top:40px; color:#999; font-size:12px;">Сгенерировано Chess Analyzer Pro</p>
            </div>
        </body>
        </html>
        """

    finally:
        # 4. ЗАКРЫВАЕМ СЕССИЮ ТОЛЬКО ЗДЕСЬ
        session.close()

    # Сохраняем файл
    filename = "report.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"✅ Отчет создан: {os.path.abspath(filename)}")
    
    # Автоматически открываем в браузере
    webbrowser.open('file://' + os.path.realpath(filename))

if __name__ == "__main__":
    generate_html_report()