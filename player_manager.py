import sqlite3
from database import DatabaseHelper

class Player:
    def __init__(self, player_id, name, phone, gender, elo_rating=1200):
        self.player_id = player_id
        self.name = name
        self.phone = phone
        self.gender = gender
        self.elo_rating = elo_rating

    def __str__(self):
        return f"[{self.player_id}] {self.name} ({self.gender}) - SĐT: {self.phone} - Elo: {self.elo_rating}"

class PlayerManager:
    def __init__(self, db_helper=None):
        # Nếu không truyền db_helper vào, nó sẽ tự tạo mới
        self.db = db_helper or DatabaseHelper()

    def add_player(self, name, phone, gender, elo_rating=1200):
        conn = self.db.connect()
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO players (name, phone, gender, elo_rating) VALUES (?, ?, ?, ?)', 
                (name, phone, gender, elo_rating)
            )
            conn.commit()
            print(f"✅ Đã thêm VĐV: {name} ({gender}) - SĐT: {phone} - Elo: {elo_rating}")
        except sqlite3.IntegrityError:
            print("❌ Lỗi: Số điện thoại này đã tồn tại trong hệ thống!")
        finally:
            conn.close()

    def get_all_players(self):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute('SELECT player_id, name, phone, gender FROM players')
        players = cursor.fetchall()
        conn.close()
        return players

    def get_enrolled_player_ids(self, tournament_id):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute('SELECT player_id FROM tournament_players WHERE tournament_id = ?', (tournament_id,))
        ids = [row[0] for row in cursor.fetchall()]
        conn.close()
        return ids

    def get_tournament_players(self, tournament_id):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT p.player_id, p.name, p.gender, p.phone 
            FROM players p
            JOIN tournament_players tp ON p.player_id = tp.player_id
            WHERE tp.tournament_id = ?
        ''', (tournament_id,))
        players = cursor.fetchall()
        conn.close()
        return players

    def update_tournament_players(self, tournament_id, player_ids):
        conn = self.db.connect()
        cursor = conn.cursor()
        try:
            cursor.execute('DELETE FROM tournament_players WHERE tournament_id = ?', (tournament_id,))
            if player_ids:
                for pid in player_ids:
                    cursor.execute(
                        'INSERT INTO tournament_players (tournament_id, player_id) VALUES (?, ?)', 
                        (tournament_id, pid)
                    )
            conn.commit()
            print(f"✅ Đã chốt danh sách {len(player_ids)} VĐV cho giải {tournament_id}")
        except Exception as e:
            print(f"❌ Lỗi cập nhật danh sách VĐV: {e}")
        finally:
            conn.close()

    def delete_player(self, player_id):
        conn = self.db.connect()
        cursor = conn.cursor()
        try:
            cursor.execute('DELETE FROM tournament_players WHERE player_id = ?', (player_id,))
            cursor.execute('DELETE FROM players WHERE player_id = ?', (player_id,))
            conn.commit()
            print(f"✅ Đã xóa VĐV có ID: {player_id}")
        except Exception as e:
            print(f"❌ Lỗi khi xóa VĐV: {e}")
        finally:
            conn.close()        