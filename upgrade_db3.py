import sqlite3

def upgrade_database():
    # Kết nối vào file database hiện tại của bạn
    conn = sqlite3.connect('pickleball.db')
    cursor = conn.cursor()

    try:
        # Tạo bảng trung gian: Lưu trữ việc VĐV nào tham gia Giải nào
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tournament_players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tournament_id INTEGER NOT NULL,
                player_id INTEGER NOT NULL,
                UNIQUE(tournament_id, player_id) -- Chống lỗi 1 VĐV đăng ký 2 lần vào cùng 1 giải
            )
        ''')
        conn.commit()
        print("✅ [THÀNH CÔNG] Đã xây xong bảng 'tournament_players' (Danh sách đăng ký)!")
    except Exception as e:
        print(f"❌ [LỖI] Có vấn đề xảy ra: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    upgrade_database()