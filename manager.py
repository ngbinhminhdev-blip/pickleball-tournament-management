import sqlite3
import sys
import io
import random
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


class Player:
    def __init__(self, player_id, name, email, elo_rating):
        self.player_id = player_id
        self.name = name
        self.email = email
        self.elo_rating = elo_rating

    def __str__(self):
        return f"[{self.player_id}] {self.name} (Elo: {self.elo_rating}) - {self.email}"

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


# ==========================================
# CLASS QUẢN LÝ LÕI (CORE MANAGER)
# ==========================================
class TournamentManager:
    def __init__(self, db_path='pickleball.db'):
        self.db_path = db_path

    def connect(self):
        return sqlite3.connect(self.db_path)

    # --- TÍNH NĂNG 1: QUẢN LÝ NGƯỜI CHƠI ---
    def add_player(self, name, phone, gender):
        conn = self.connect()
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO players (name, phone, gender) VALUES (?, ?, ?)', (name, phone, gender))
            conn.commit()
            print(f"Đã thêm: {name} ({gender}) - SĐT: {phone}")
        except sqlite3.IntegrityError:
            print("Số điện thoại này đã tồn tại!")
        finally:
            conn.close()

    def get_enrolled_player_ids(self, tournament_id):
        """Lấy ra ID của các VĐV đã đăng ký giải này (dùng để tích sẵn checkbox)"""
        conn = self.connect()
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT player_id FROM tournament_players WHERE tournament_id = ?', (tournament_id,))
            return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            print(f"❌ Lỗi lấy ID VĐV: {e}")
            return []
        finally:
            conn.close()

    def get_tournament_players(self, tournament_id):
        """Lấy chi tiết thông tin VĐV thực sự tham gia giải này (để bốc thăm)"""
        conn = self.connect()
        cursor = conn.cursor()
        try:
            # Kết nối bảng tournament_players và bảng players (kho tổng)
            cursor.execute('''
                SELECT p.id, p.name, p.gender, p.phone 
                FROM players p
                JOIN tournament_players tp ON p.id = tp.player_id
                WHERE tp.tournament_id = ?
            ''', (tournament_id,))
            return cursor.fetchall()
        except Exception as e:
            print(f"❌ Lỗi lấy danh sách VĐV của giải: {e}")
            return []
        finally:
            conn.close()

    def update_tournament_players(self, tournament_id, player_ids):
        """Lưu danh sách VĐV do Ban Tổ Chức vừa tích chọn"""
        conn = self.connect()
        cursor = conn.cursor()
        try:
            # Bước A: Xóa danh sách đăng ký cũ của giải này cho sạch sẽ
            cursor.execute('DELETE FROM tournament_players WHERE tournament_id = ?', (tournament_id,))
            
            # Bước B: Lưu danh sách mới mà bạn vừa tích chọn
            if player_ids:
                for pid in player_ids:
                    cursor.execute('''
                        INSERT INTO tournament_players (tournament_id, player_id) 
                        VALUES (?, ?)
                    ''', (tournament_id, pid))
            conn.commit()
            print(f"✅ Đã chốt danh sách {len(player_ids)} VĐV cho giải {tournament_id}")
        except Exception as e:
            print(f"❌ Lỗi cập nhật danh sách VĐV: {e}")
        finally:
            conn.close()        

    def get_all_players(self):
        conn = self.connect()
        cursor = conn.cursor()
        # Chỉ định rõ thứ tự các cột muốn lấy ra
        cursor.execute('SELECT player_id, name, phone, gender FROM players')
        players = cursor.fetchall()
        conn.close()
        return players
    
    def get_all_teams(self):
        conn = self.connect()
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

    # --- TÍNH NĂNG 2: QUẢN LÝ ĐỘI ---
    def create_team(self, player1_id, player2_id=None):
        conn = self.connect()
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO teams (player1_id, player2_id) VALUES (?, ?)', (player1_id, player2_id))
            conn.commit()
            print(f"[SUCCESS] Đã tạo Đội thành công!")
        except Exception as e:
            print(f"[FAILED] Lỗi tạo đội: {e}")
        finally:
            conn.close()


    # --- TÍNH NĂNG 3: XẾP LỊCH THI ĐẤU VÒNG TRÒN ---
    def create_tournament(self, title, format_type):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO tournaments (title, format) VALUES (?, ?)', (title, format_type))
        tournament_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return tournament_id


    def show_matches(self, tournament_id):
        """Hiển thị danh sách các trận đấu, bao gồm cả Vòng bảng và Tỉ số"""
        conn = self.connect()
        cursor = conn.cursor()
        
        # Bổ sung lấy thêm cột 'stage' từ database
        cursor.execute('''
            SELECT match_id, team_a_id, team_b_id, score_a, score_b, winner_team_id, stage 
            FROM matches WHERE tournament_id = ?
        ''', (tournament_id,))
        rows = cursor.fetchall()
        conn.close()

        print(f"\n--- BẢNG KẾT QUẢ THI ĐẤU (GIẢI ID: {tournament_id}) ---")
        for row in rows:
            # Gán thêm biến stage vào cuối
            m_id, t_a, t_b, s_a, s_b, winner, stage = row
            
            # Xử lý hiển thị Tỉ số
            if winner is not None:
                status = f"Tỉ số: [{s_a} - {s_b}] => Đội {winner} THẮNG"
            else:
                status = "Chưa thi đấu"
            
            # Xử lý hiển thị Vòng bảng (Nếu có)
            stage_info = f" ({stage})" if stage else ""
                
            print(f"Trận {m_id}{stage_info}: Đội {t_a} vs Đội {t_b} | {status}")

    # --- TÍNH NĂNG: TẠO VÒNG BÁN KẾT (KNOCKOUT) ---

    def get_matches(self, tournament_id):
        """Lấy danh sách trận đấu trả về cho Web"""
        conn = self.connect()
        cursor = conn.cursor()
        # Trả lại tên tournament_id cho đúng với Database của bạn
        cursor.execute('''
            SELECT match_id, team_a_id, team_b_id, score_a, score_b, winner_team_id, stage 
            FROM matches WHERE tournament_id = ?
        ''', (tournament_id,))
        matches = cursor.fetchall()
        conn.close()
        return matches


    # ======================================================
    # 1. HÀM TẠO BẢNG A & B VÀ ĐÁ VÒNG TRÒN
    # ======================================================
    def generate_group_stage(self, tournament_id):
        conn = self.connect()
        cursor = conn.cursor()
        
        # 1. DỌN SẠCH KHO CHO GIẢI NÀY TRƯỚC KHI TẠO MỚI (Tránh kẹt ID hoặc rác tàng hình)
        cursor.execute("DELETE FROM matches WHERE tournament_id = ?", (tournament_id,))
        
        # 2. LẤY DANH SÁCH ĐỘI
        cursor.execute('SELECT team_id FROM teams')
        teams = [row[0] for row in cursor.fetchall()]
        
        if len(teams) < 4:
            print("❌ Cảnh báo: Không đủ 4 đội để chia bảng!")
            conn.close()
            return

        # 3. CHIA BẢNG NGẪU NHIÊN
        import random
        random.shuffle(teams)
        mid = len(teams) // 2
        group_a = teams[:mid]
        group_b = teams[mid:]

        # 4. GOM TRẬN ĐẤU (Sử dụng đúng cấu trúc của hàm Vòng tròn)
        matches = []
        for i in range(len(group_a)):
            for j in range(i + 1, len(group_a)):
                # Đảm bảo tournament_id được nhét vào đúng vị trí đầu tiên
                matches.append((tournament_id, group_a[i], group_a[j], 'Bảng A'))
                
        for i in range(len(group_b)):
            for j in range(i + 1, len(group_b)):
                matches.append((tournament_id, group_b[i], group_b[j], 'Bảng B'))

        # 5. ÉP LƯU VÀO DATABASE BẰNG EXECUTEMANY
        cursor.executemany('INSERT INTO matches (tournament_id, team_a_id, team_b_id, stage) VALUES (?, ?, ?, ?)', matches)
        conn.commit()
        
        # 6. MÁY QUÉT KIỂM TRA LẠI SAU KHI LƯU
        cursor.execute('SELECT count(*) FROM matches WHERE tournament_id = ?', (tournament_id,))
        count = cursor.fetchone()[0]
        print(f"✅ BÁO CÁO NHANH: Đã lưu thành công {count} trận của giải {tournament_id} vào Database!")
        
        conn.close()

    # ==========================================
    # CHẾ ĐỘ 2: ĐÁ VÒNG TRÒN (1 BẢNG CHUNG)
    # ==========================================
    def generate_round_robin(self, tournament_id):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('SELECT team_id FROM teams')
        teams = [row[0] for row in cursor.fetchall()]
        if len(teams) < 4: return
        
        matches = []
        for i in range(len(teams)):
            for j in range(i + 1, len(teams)):
                matches.append((tournament_id, teams[i], teams[j], 'Vòng bảng'))
                
        import random
        random.shuffle(matches)
        cursor.executemany('INSERT INTO matches (tournament_id, team_a_id, team_b_id, stage) VALUES (?, ?, ?, ?)', matches)
        conn.commit()
        conn.close()    

    # ======================================================
    # 2. HÀM CHỐT BÁN KẾT (Nhất A vs Nhì B)
    # ======================================================
    def generate_semi_finals_group(self, tournament_id):
        print("\n--- [HỆ THỐNG] ĐÃ NHẬN LỆNH CHỐT BÁN KẾT ---")
        conn = self.connect()
        cursor = conn.cursor()
        try:
            def get_top_2(stage_name):
                print(f"Đang tính điểm cho {stage_name}...")
                cursor.execute('''
                    SELECT team_a_id, team_b_id, winner_team_id 
                    FROM matches 
                    WHERE stage = ? AND tournament_id = ?
                ''', (stage_name, tournament_id))
                matches = cursor.fetchall()
                print(f"Tìm thấy {len(matches)} trận đã đá ở {stage_name}")
                
                scores = {}
                for team_a, team_b, winner in matches:
                    if team_a not in scores: scores[team_a] = 0
                    if team_b not in scores: scores[team_b] = 0
                    if winner:
                        scores[winner] = scores.get(winner, 0) + 1
                
                # Sắp xếp theo số trận thắng giảm dần
                ranked_teams = sorted(scores.keys(), key=lambda t: scores[t], reverse=True)
                return ranked_teams

            top_a = get_top_2('Bảng A')
            top_b = get_top_2('Bảng B')
            
            print(f"Top Bảng A (Nhất - Nhì): {top_a[:2] if len(top_a)>=2 else top_a}")
            print(f"Top Bảng B (Nhất - Nhì): {top_b[:2] if len(top_b)>=2 else top_b}")

            if len(top_a) < 2 or len(top_b) < 2:
                print("❌ LỖI: Mỗi bảng phải có ít nhất 2 đội đã đá và có kết quả thắng/thua!")
                return

            # Xóa bán kết cũ của giải này nếu có để tránh trùng
            cursor.execute("DELETE FROM matches WHERE stage IN ('Bán kết 1', 'Bán kết 2') AND tournament_id = ?", (tournament_id,))

            # Xếp lịch Nhất A - Nhì B và Nhất B - Nhì A
            semi_matches = [
                (tournament_id, top_a[0], top_b[1], 'Bán kết 1'),
                (tournament_id, top_b[0], top_a[1], 'Bán kết 2')
            ]
            
            cursor.executemany('INSERT INTO matches (tournament_id, team_a_id, team_b_id, stage) VALUES (?, ?, ?, ?)', semi_matches)
            conn.commit()
            print("✅ XẾP LỊCH BÁN KẾT THÀNH CÔNG!")
        except Exception as e:
            print(f"❌ LỖI DATABASE: {e}")
        finally:
            conn.close()

    def generate_third_place(self, tournament_id):
        """Xếp lịch trận Tranh hạng 3 (Xóa rác cũ, ép tạo mới)"""
        conn = self.connect()
        cursor = conn.cursor()
        try:
            # Lấy 2 trận Bán kết đã có người thắng
            cursor.execute('''
                SELECT team_a_id, team_b_id, winner_team_id 
                FROM matches 
                WHERE tournament_id = ? 
                AND stage IN ('Bán kết 1', 'Bán kết 2') 
                AND winner_team_id IS NOT NULL 
                AND winner_team_id != ''
            ''', (tournament_id,))
            semis = cursor.fetchall()
            
            if len(semis) >= 2:
                # Lấy 2 trận bán kết cuối cùng (chuẩn xác nhất)
                s1, s2 = semis[-2], semis[-1]
                
                # Ép kiểu chữ để so sánh không bao giờ sai
                team_a_1, team_b_1, win_1 = str(s1[0]), str(s1[1]), str(s1[2])
                team_a_2, team_b_2, win_2 = str(s2[0]), str(s2[1]), str(s2[2])

                # Tìm đội thua ở Bán kết
                loser1 = team_a_1 if win_1 == team_b_1 else team_b_1
                loser2 = team_a_2 if win_2 == team_b_2 else team_b_2
                
                # QUAN TRỌNG NHẤT: Xóa sạch trận Tranh hạng 3 "rác" cũ nếu có
                cursor.execute('DELETE FROM matches WHERE tournament_id = ? AND stage = ?', (tournament_id, 'Tranh hạng 3'))
                
                # Tạo trận mới toanh
                cursor.execute('''
                    INSERT INTO matches (tournament_id, team_a_id, team_b_id, stage)
                    VALUES (?, ?, ?, 'Tranh hạng 3')
                ''', (tournament_id, loser1, loser2))
                conn.commit()
                print(f"✅ Đã dọn rác và chốt Tranh hạng 3: {loser1} vs {loser2}")
        except Exception as e:
            print(f"❌ Lỗi tạo Tranh hạng 3: {e}")
        finally:
            conn.close()

    def generate_final_only(self, tournament_id):
        """Xếp lịch trận Chung kết (Xóa rác cũ, ép tạo mới)"""
        conn = self.connect()
        cursor = conn.cursor()
        try:
            # Lấy người thắng từ Bán kết
            cursor.execute('''
                SELECT winner_team_id 
                FROM matches 
                WHERE tournament_id = ? 
                AND stage IN ('Bán kết 1', 'Bán kết 2') 
                AND winner_team_id IS NOT NULL 
                AND winner_team_id != ''
            ''', (tournament_id,))
            winners = [str(row[0]) for row in cursor.fetchall()]
            
            if len(winners) >= 2:
                win1, win2 = winners[-2], winners[-1]
                
                # QUAN TRỌNG NHẤT: Xóa sạch trận Chung kết "rác" cũ
                cursor.execute('DELETE FROM matches WHERE tournament_id = ? AND stage = ?', (tournament_id, 'Chung kết'))
                
                # Tạo trận mới toanh
                cursor.execute('''
                    INSERT INTO matches (tournament_id, team_a_id, team_b_id, stage)
                    VALUES (?, ?, ?, 'Chung kết')
                ''', (tournament_id, win1, win2))
                conn.commit()
                print(f"✅ Đã dọn rác và chốt Chung kết: {win1} vs {win2}")
        except Exception as e:
            print(f"❌ Lỗi tạo Chung kết: {e}")
        finally:
            conn.close()   

    # --- TÍNH NĂNG 4: CẬP NHẬT TỈ SỐ ---
    def update_score(self, match_id, score_a, score_b):
        """Cập nhật tỉ số và tự động xác định đội chiến thắng"""
        conn = self.connect()
        cursor = conn.cursor()

        # 1. Lấy thông tin 2 đội trong trận đấu này
        cursor.execute('SELECT team_a_id, team_b_id FROM matches WHERE match_id = ?', (match_id,))
        match = cursor.fetchone()
        
        if not match:
            print(f"[FAILED] Không tìm thấy Trận đấu số {match_id}!")
            conn.close()
            return

        team_a_id = match[0]
        team_b_id = match[1]

        # 2. So sánh điểm để tìm đội thắng (Pickleball thường không có hòa)
        winner_id = None
        if score_a > score_b:
            winner_id = team_a_id
        elif score_b > score_a:
            winner_id = team_b_id

        # 3. Cập nhật dữ liệu vào bảng matches
        cursor.execute('''
            UPDATE matches 
            SET score_a = ?, score_b = ?, winner_team_id = ?
            WHERE match_id = ?
        ''', (score_a, score_b, winner_id, match_id))
        
        conn.commit()
        conn.close()
        print(f"[SUCCESS] Đã cập nhật Trận {match_id}: Đội {team_a_id} ({score_a}) - ({score_b}) Đội {team_b_id}")   

    # --- TÍNH NĂNG 5: BẢNG XẾP HẠNG ---
    def show_leaderboard(self, tournament_id):
        """Tính toán và hiển thị Bảng xếp hạng của giải đấu"""
        conn = self.connect()
        cursor = conn.cursor()

        # Lấy tất cả các trận đấu ĐÃ CÓ KẾT QUẢ của giải này
        cursor.execute('''
            SELECT team_a_id, team_b_id, winner_team_id
            FROM matches 
            WHERE tournament_id = ? AND winner_team_id IS NOT NULL
        ''', (tournament_id,))
        matches = cursor.fetchall()
        conn.close()

        # Dùng Dictionary để đếm số trận thắng
        # Cấu trúc: {team_id: số_trận_thắng}
        leaderboard = {}

        for match in matches:
            t_a, t_b, winner = match
            
            # Đảm bảo 2 đội đều có tên trong bảng xếp hạng (khởi tạo = 0)
            if t_a not in leaderboard:
                leaderboard[t_a] = 0
            if t_b not in leaderboard:
                leaderboard[t_b] = 0
            
            # Cộng 1 điểm cho đội chiến thắng
            leaderboard[winner] += 1

        # Sắp xếp bảng xếp hạng theo số trận thắng (Từ cao xuống thấp)
        # Sử dụng hàm sorted và cú pháp lambda (hàm ẩn danh) của Python
        sorted_leaderboard = sorted(leaderboard.items(), key=lambda item: item[1], reverse=True)

        print(f"\n🏆 --- BẢNG XẾP HẠNG (GIẢI ID: {tournament_id}) --- 🏆")
        if not sorted_leaderboard:
            print("Chưa có dữ liệu xếp hạng (các trận chưa đấu).")
            return

        rank = 1
        for team_id, wins in sorted_leaderboard:
            print(f"Hạng {rank} | Đội {team_id} | Thắng: {wins} trận")
            rank += 1         
    
    # 1. Sửa hàm add_player để nhận thêm Giới tính
    def add_player(self, name, phone, gender):
        conn = self.connect()
        cursor = conn.cursor()
        try:
            # Nhớ đổi chữ email thành phone ở 2 vị trí trong dòng dưới này nhé:
            cursor.execute('INSERT INTO players (name, phone, gender) VALUES (?, ?, ?)', (name, phone, gender))
            conn.commit()
            print(f"Đã thêm: {name} ({gender}) - SĐT: {phone}")
        except sqlite3.IntegrityError:
            print("Số điện thoại này đã tồn tại!")
        finally:
            conn.close()

    # --- THUẬT TOÁN BỐC THĂM ĐỘI NGẪU NHIÊN ---
    def create_team(self, player1_id, player2_id):
        """Hàm lưu đội vào Database"""
        conn = self.connect()
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO teams (player1_id, player2_id) VALUES (?, ?)', (player1_id, player2_id))
            conn.commit()
            print(f"✅ Đã tạo đội thành công: VĐV {player1_id} + VĐV {player2_id}")
        except Exception as e:
            print(f"❌ Lỗi khi tạo đội: {e}")
        finally:
            conn.close()

    def auto_pair_mixed(self):
        """Bốc thăm Đôi Nam - Nữ"""
        import random
        conn = self.connect()
        cursor = conn.cursor()
        
        # Dùng TRIM() để đề phòng lỗi dư khoảng trắng khi nhập liệu
        cursor.execute("SELECT player_id FROM players WHERE trim(gender) = 'Nam'")
        males = [row[0] for row in cursor.fetchall()]
        
        cursor.execute("SELECT player_id FROM players WHERE trim(gender) = 'Nữ'")
        females = [row[0] for row in cursor.fetchall()]
        
        print(f"\n👉 Đang bốc thăm Nam-Nữ... Tìm thấy {len(males)} Nam và {len(females)} Nữ.")
        
        random.shuffle(males)
        random.shuffle(females)
        
        # Ghép cặp (ai thừa ra thì chịu)
        pairs_count = min(len(males), len(females))
        for i in range(pairs_count):
            self.create_team(males[i], females[i])
            
        print(f"🎉 Bốc thăm Nam-Nữ hoàn tất! Ghép được {pairs_count} đội.")
        conn.close()

    def auto_pair_same_gender(self, target_gender):
        """Bốc thăm Đôi Nam-Nam hoặc Nữ-Nữ"""
        import random
        conn = self.connect()
        cursor = conn.cursor()
        
        # Dùng TRIM() để đảm bảo khớp chữ chính xác 100%
        cursor.execute("SELECT player_id FROM players WHERE trim(gender) = ?", (target_gender,))
        players = [row[0] for row in cursor.fetchall()]
        
        print(f"\n👉 Đang bốc thăm {target_gender}... Tìm thấy {len(players)} VĐV.")
        
        random.shuffle(players)
        
        # Cứ 2 người đứng cạnh nhau thì gom thành 1 đội
        count = 0
        for i in range(0, len(players) - 1, 2):
            self.create_team(players[i], players[i+1])
            count += 1
            
        print(f"🎉 Bốc thăm {target_gender} hoàn tất! Ghép được {count} đội.")
        conn.close()
    
    # Lấy danh sách tất cả các giải đấu
    def get_all_tournaments(self):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM tournaments')
        tours = cursor.fetchall()
        conn.close()
        return tours

    # Tạo giải đấu mới với tên tùy chọn
    def create_tournament(self, name):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO tournaments (name) VALUES (?)', (name,))
        conn.commit()
        conn.close()

    def clear_all_teams(self):
        conn = self.connect()
        cursor = conn.cursor()
        try:
            # Phải xóa các trận đấu cũ trước vì nó dính líu đến Đội
            cursor.execute('DELETE FROM matches') 
            # Xóa sạch sành sanh danh sách đội
            cursor.execute('DELETE FROM teams')
            
            # Reset lại số thứ tự ID đội về lại từ số 1 (Để không bị tình trạng xóa xong tạo lại ra Đội 99)
            cursor.execute('DELETE FROM sqlite_sequence WHERE name="teams"')
            cursor.execute('DELETE FROM sqlite_sequence WHERE name="matches"')
            
            conn.commit()
            print("✅ Đã dọn dẹp sạch sẽ toàn bộ Đội và Lịch thi đấu!")
        except Exception as e:
            print(f"❌ Lỗi khi xóa: {e}")
        finally:
            conn.close()  

    def update_score_bo3(self, match_id, s1a, s1b, s2a, s2b, s3a, s3b):
        conn = self.connect()
        cursor = conn.cursor()
        try:
            # 1. Đếm số set thắng của từng đội
            sets_a = 0
            sets_b = 0
            if s1a > s1b: sets_a += 1
            elif s1b > s1a: sets_b += 1
            
            if s2a > s2b: sets_a += 1
            elif s2b > s2a: sets_b += 1
            
            if s3a > s3b: sets_a += 1
            elif s3b > s3a: sets_b += 1
            
            # 2. Lấy ID hai đội để xem ai là người chiến thắng
            cursor.execute('SELECT team_a_id, team_b_id FROM matches WHERE match_id = ?', (match_id,))
            row = cursor.fetchone()
            if not row: return
            
            team_a_id, team_b_id = row
            winner_id = team_a_id if sets_a > sets_b else team_b_id
            
            # 3. Lưu điểm chi tiết 3 set, và dùng cột score_a/score_b để lưu Tỉ số Set (VD: 2-1)
            cursor.execute('''
                UPDATE matches 
                SET score_a = ?, score_b = ?, 
                    set1_a = ?, set1_b = ?, 
                    set2_a = ?, set2_b = ?, 
                    set3_a = ?, set3_b = ?,
                    winner_team_id = ?
                WHERE match_id = ?
            ''', (sets_a, sets_b, s1a, s1b, s2a, s2b, s3a, s3b, winner_id, match_id))
            
            conn.commit()
            print(f"✅ Đã lưu tỉ số BO3 trận {match_id}: Đội {team_a_id} ({sets_a}) - ({sets_b}) Đội {team_b_id}")
        except Exception as e:
            print(f"❌ Lỗi cập nhật điểm BO3: {e}")
        finally:
            conn.close()     

    def delete_tournament(self, tournament_id):
        """Xóa giải đấu (Tự động dò tên cột ID)"""
        conn = self.connect()
        cursor = conn.cursor()
        try:
            cursor.execute('DELETE FROM matches WHERE tournament_id = ?', (int(tournament_id),))
        
            try:
                cursor.execute('DELETE FROM tournaments WHERE id = ?', (int(tournament_id),))
            except:
                try:
                    cursor.execute('DELETE FROM tournaments WHERE tournament_id = ?', (int(tournament_id),))
                except:
                    cursor.execute('DELETE FROM tournaments WHERE tournament_id = ?', (int(tournament_id),))
                    
            conn.commit()
        except Exception as e:
            raise e
        finally:
            conn.close() 

if __name__ == "__main__":
    manager = TournamentManager()    
    print("\n--- 1. KHỞI TẠO GIẢI ĐẤU & XẾP LỊCH BẢNG ---")
    tournament_id = manager.create_tournament("Cúp Pickleball Vô Địch Mùa Hè", "Group + Knockout")
    manager.generate_group_stage(tournament_id)

    print("\n--- 2. KẾT QUẢ VÒNG BẢNG ---")
    manager.update_score(match_id=1, score_a=11, score_b=8)
    manager.update_score(match_id=2, score_a=5, score_b=11)
    
    print("\n--- 3. CHIA NHÁNH BÁN KẾT ---")
    manager.generate_semi_finals(tournament_id)
    
    print("\n--- 4. TRỌNG TÀI NHẬP KẾT QUẢ BÁN KẾT ---")
    manager.update_score(match_id=3, score_a=15, score_b=13)
    manager.update_score(match_id=4, score_a=9, score_b=11)

    print("\n--- 5. TẠO LỊCH CHUNG KẾT ---")
    manager.generate_finals(tournament_id)

    print("\n--- 6. KẾT QUẢ TRẬN CHUNG KẾT ---")
    manager.update_score(match_id=5, score_a=11, score_b=7) # Đội thắng cúp!
    manager.update_score(match_id=6, score_a=11, score_b=9)

    print("\n🏆 BẢNG TỔNG SẮP TOÀN GIẢI ĐẤU 🏆")
    manager.show_matches(tournament_id)