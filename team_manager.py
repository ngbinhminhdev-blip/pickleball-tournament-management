import random
from database import DatabaseHelper

class Team:
    def __init__(self, team_id, player1_name, player2_name=None):
        self.team_id = team_id
        self.player1_name = player1_name
        self.player2_name = player2_name

    def __str__(self):
        if self.player2_name:
            return f"[Đội {self.team_id}] {self.player1_name} & {self.player2_name} (Đôi)"
        else:
            return f"[Đội {self.team_id}] {self.player1_name} (Đơn)"

class TeamManager:
    def __init__(self, db_helper=None):
        self.db = db_helper or DatabaseHelper()

    def get_all_teams(self):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT t.team_id, p1.name, p2.name
            FROM teams t
            JOIN players p1 ON t.player1_id = p1.player_id
            JOIN players p2 ON t.player2_id = p2.player_id
        ''')
        teams = cursor.fetchall()
        conn.close()
        return teams

    def create_team(self, player1_id, player2_id=None):
        conn = self.db.connect()
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO teams (player1_id, player2_id) VALUES (?, ?)', (player1_id, player2_id))
            conn.commit()
            print(f"✅ Đã tạo đội thành công: VĐV {player1_id} + VĐV {player2_id}")
        except Exception as e:
            print(f"❌ Lỗi tạo đội: {e}")
        finally:
            conn.close()

    def auto_pair_mixed(self):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT player_id FROM players WHERE trim(gender) = 'Nam'")
        males = [row[0] for row in cursor.fetchall()]
        
        cursor.execute("SELECT player_id FROM players WHERE trim(gender) = 'Nữ'")
        females = [row[0] for row in cursor.fetchall()]
        
        print(f"\n👉 Đang bốc thăm Nam-Nữ... Tìm thấy {len(males)} Nam và {len(females)} Nữ.")
        random.shuffle(males)
        random.shuffle(females)
        
        pairs_count = min(len(males), len(females))
        for i in range(pairs_count):
            self.create_team(males[i], females[i])
            
        print(f"🎉 Bốc thăm Nam-Nữ hoàn tất! Ghép được {pairs_count} đội.")
        conn.close()

    def auto_pair_same_gender(self, target_gender):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT player_id FROM players WHERE trim(gender) = ?", (target_gender,))
        players = [row[0] for row in cursor.fetchall()]
        
        print(f"\n👉 Đang bốc thăm {target_gender}... Tìm thấy {len(players)} VĐV.")
        random.shuffle(players)
        
        count = 0
        for i in range(0, len(players) - 1, 2):
            self.create_team(players[i], players[i+1])
            count += 1
            
        print(f"🎉 Bốc thăm {target_gender} hoàn tất! Ghép được {count} đội.")
        conn.close()

    def clear_all_teams(self):
        conn = self.db.connect()
        cursor = conn.cursor()
        try:
            cursor.execute('DELETE FROM matches') 
            cursor.execute('DELETE FROM teams')
            cursor.execute('DELETE FROM sqlite_sequence WHERE name="teams"')
            cursor.execute('DELETE FROM sqlite_sequence WHERE name="matches"')
            conn.commit()
            print("✅ Đã dọn dẹp sạch sẽ toàn bộ Đội và Lịch thi đấu!")
        except Exception as e:
            print(f"❌ Lỗi khi xóa: {e}")
        finally:
            conn.close()