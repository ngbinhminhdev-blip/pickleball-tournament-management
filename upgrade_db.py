import sqlite3

def upgrade():
    conn = sqlite3.connect('pickleball.db')
    cursor = conn.cursor()
    
    # Danh sách 6 cột cần thêm cho 3 Set đấu (Điểm của Đội A và Đội B)
    new_columns = ['set1_a', 'set1_b', 'set2_a', 'set2_b', 'set3_a', 'set3_b']
    
    for col in new_columns:
        try:
            cursor.execute(f'ALTER TABLE matches ADD COLUMN {col} INTEGER DEFAULT 0')
            print(f"✅ Đã thêm cột {col}")
        except sqlite3.OperationalError:
            print(f"⚠️ Cột {col} đã có sẵn, bỏ qua.")
            
    conn.commit()
    conn.close()
    print("🎉 Nâng cấp Database thành công! Đã sẵn sàng cho kèo Best of 3.")

if __name__ == '__main__':
    upgrade()