import sqlite3

def upgrade_database():
    conn = sqlite3.connect("pickleball.db")
    cursor = conn.cursor()

    # 1. Thêm các cột điểm BO3 vào bảng matches
    score_columns = [
        "set1_a", "set1_b",
        "set2_a", "set2_b",
        "set3_a", "set3_b",
    ]

    for column in score_columns:
        try:
            cursor.execute(f"ALTER TABLE matches ADD COLUMN {column} INTEGER DEFAULT 0")
            print(f"✅ Đã thêm cột: {column}")
        except sqlite3.OperationalError:
            print(f"ℹ️ Cột '{column}' đã tồn tại.")

    # 2. Thêm cột tournament_id vào bảng matches
    try:
        cursor.execute("ALTER TABLE matches ADD COLUMN tournament_id INTEGER DEFAULT 1")
        print("✅ Đã thêm cột: tournament_id")
    except sqlite3.OperationalError:
        print("ℹ️ Cột 'tournament_id' đã tồn tại.")

    # 3. Thêm cột elo_rating vào bảng players (Cập nhật mới nhất)
    try:
        cursor.execute("ALTER TABLE players ADD COLUMN elo_rating INTEGER DEFAULT 1200")
        print("✅ Đã thêm cột: elo_rating vào bảng players")
    except sqlite3.OperationalError:
        print("ℹ️ Cột 'elo_rating' đã tồn tại.")

    # 4. Tạo bảng tournament_players (Dùng để quản lý người chơi trong từng giải)
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tournament_players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tournament_id INTEGER NOT NULL,
                player_id INTEGER NOT NULL,
                UNIQUE(tournament_id, player_id)
            )
        """)
        print("✅ Đã kiểm tra/Tạo bảng: tournament_players")
    except Exception as e:
        print(f"❌ Lỗi khi tạo bảng tournament_players: {e}")

    conn.commit()
    conn.close()

    print("🎉 Quá trình nâng cấp Database hoàn tất!")

if __name__ == "__main__":
    upgrade_database()