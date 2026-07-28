import sqlite3

def upgrade():
    conn = sqlite3.connect('pickleball.db')
    cursor = conn.cursor()
    
    try:
        # Thêm cột tour_id để phân biệt các giải đấu với nhau
        cursor.execute('ALTER TABLE matches ADD COLUMN tour_id INTEGER DEFAULT 1')
        print("✅ Nâng cấp móng nhà thành công: Đã thêm cột tour_id!")
    except sqlite3.OperationalError:
        print("⚠️ Cột tour_id đã có sẵn, không cần thêm nữa.")
        
    conn.commit()
    conn.close()

if __name__ == '__main__':
    upgrade()