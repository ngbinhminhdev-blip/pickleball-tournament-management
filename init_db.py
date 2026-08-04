import sqlite3

def create_tables():
    conn = sqlite3.connect('pickleball.db')
    cursor = conn.cursor()

    # 1. Bảng Vận động viên (Đã thêm elo_rating)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
            player_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT UNIQUE NOT NULL,
            gender TEXT NOT NULL,
            elo_rating INTEGER DEFAULT 1200
        )
    ''')

    # 2. Bảng Đội thi đấu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teams (
            team_id INTEGER PRIMARY KEY AUTOINCREMENT,
            player1_id INTEGER,
            player2_id INTEGER
        )
    ''')

    # 3. Bảng Giải đấu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tournaments (
            tournament_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            format TEXT
        )
    ''')

    # 4. Bảng Lịch thi đấu (Hỗ trợ đá Vòng bảng & BO3)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS matches (
            match_id INTEGER PRIMARY KEY AUTOINCREMENT,
            tournament_id INTEGER,
            team_a_id INTEGER,
            team_b_id INTEGER,
            score_a INTEGER DEFAULT 0,
            score_b INTEGER DEFAULT 0,
            set1_a INTEGER, set1_b INTEGER,
            set2_a INTEGER, set2_b INTEGER,
            set3_a INTEGER, set3_b INTEGER,
            winner_team_id INTEGER,
            stage TEXT
        )
    ''')

    # 5. Bảng Trung gian: Danh sách VĐV đăng ký tham gia một giải cụ thể
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tournament_players (
            tournament_id INTEGER,
            player_id INTEGER
        )
    ''')

    conn.commit()
    conn.close()
    print("✅ Đã khởi tạo cấu trúc Database thành công!")

if __name__ == "__main__":
    create_tables()