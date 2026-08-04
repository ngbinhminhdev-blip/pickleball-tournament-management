from database import DatabaseHelper

class MatchManager:
    def __init__(self, db_helper=None):
        self.db = db_helper or DatabaseHelper()

    # ==========================================
    # QUẢN LÝ GIẢI ĐẤU (TOURNAMENTS)
    # ==========================================
    def get_all_tournaments(self):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM tournaments')
        tours = cursor.fetchall()
        conn.close()
        return tours

    def create_tournament(self, title, format_type):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO tournaments (title, format) VALUES (?, ?)', (title, format_type))
        tournament_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return tournament_id

    def delete_tournament(self, tournament_id):
        conn = self.db.connect()
        cursor = conn.cursor()
        try:
            cursor.execute('DELETE FROM matches WHERE tournament_id = ?', (int(tournament_id),))
            try:
                cursor.execute('DELETE FROM tournaments WHERE id = ?', (int(tournament_id),))
            except:
                cursor.execute('DELETE FROM tournaments WHERE tournament_id = ?', (int(tournament_id),))
            conn.commit()
            print(f"✅ Đã xóa giải đấu {tournament_id}")
        except Exception as e:
            print(f"❌ Lỗi xóa giải đấu: {e}")
        finally:
            conn.close()

    # ==========================================
    # HIỂN THỊ KẾT QUẢ & XẾP HẠNG
    # ==========================================
    def show_matches(self, tournament_id):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT match_id, team_a_id, team_b_id, score_a, score_b, winner_team_id, stage 
            FROM matches WHERE tournament_id = ?
        ''', (tournament_id,))
        rows = cursor.fetchall()
        conn.close()

        print(f"\n--- BẢNG KẾT QUẢ THI ĐẤU (GIẢI ID: {tournament_id}) ---")
        for row in rows:
            m_id, t_a, t_b, s_a, s_b, winner, stage = row
            if winner is not None:
                status = f"Tỉ số: [{s_a} - {s_b}] => Đội {winner} THẮNG"
            else:
                status = "Chưa thi đấu"
            stage_info = f" ({stage})" if stage else ""
            print(f"Trận {m_id}{stage_info}: Đội {t_a} vs Đội {t_b} | {status}")

    def get_matches(self, tournament_id):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT match_id, team_a_id, team_b_id, score_a, score_b, winner_team_id, stage 
            FROM matches WHERE tournament_id = ?
        ''', (tournament_id,))
        matches = cursor.fetchall()
        conn.close()
        return matches

    def show_leaderboard(self, tournament_id):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT team_a_id, team_b_id, winner_team_id
            FROM matches 
            WHERE tournament_id = ? AND winner_team_id IS NOT NULL
        ''', (tournament_id,))
        matches = cursor.fetchall()
        conn.close()

        leaderboard = {}
        for match in matches:
            t_a, t_b, winner = match
            if t_a not in leaderboard: leaderboard[t_a] = 0
            if t_b not in leaderboard: leaderboard[t_b] = 0
            leaderboard[winner] += 1

        sorted_leaderboard = sorted(leaderboard.items(), key=lambda item: item[1], reverse=True)

        print(f"\n🏆 --- BẢNG XẾP HẠNG (GIẢI ID: {tournament_id}) --- 🏆")
        if not sorted_leaderboard:
            print("Chưa có dữ liệu xếp hạng (các trận chưa đấu).")
            return

        rank = 1
        for team_id, wins in sorted_leaderboard:
            print(f"Hạng {rank} | Đội {team_id} | Thắng: {wins} trận")
            rank += 1        

    # ==========================================
    # CẬP NHẬT TỈ SỐ
    # ==========================================
    def update_score(self, match_id, score_a, score_b):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute('SELECT team_a_id, team_b_id FROM matches WHERE match_id = ?', (match_id,))
        match = cursor.fetchone()
        
        if not match:
            print(f"❌ Không tìm thấy Trận đấu số {match_id}!")
            conn.close()
            return

        team_a_id, team_b_id = match
        winner_id = team_a_id if score_a > score_b else (team_b_id if score_b > score_a else None)

        cursor.execute('''
            UPDATE matches 
            SET score_a = ?, score_b = ?, winner_team_id = ?
            WHERE match_id = ?
        ''', (score_a, score_b, winner_id, match_id))
        conn.commit()
        conn.close()
        print(f"✅ Đã cập nhật Trận {match_id}: Đội {team_a_id} ({score_a}) - ({score_b}) Đội {team_b_id}")   

    def update_score_bo3(self, match_id, s1a, s1b, s2a, s2b, s3a, s3b):
        conn = self.db.connect()
        cursor = conn.cursor()
        try:
            sets_a = sum([s1a > s1b, s2a > s2b, s3a > s3b])
            sets_b = sum([s1b > s1a, s2b > s2a, s3b > s3a])
            
            cursor.execute('SELECT team_a_id, team_b_id FROM matches WHERE match_id = ?', (match_id,))
            row = cursor.fetchone()
            if not row: return
            
            team_a_id, team_b_id = row
            winner_id = team_a_id if sets_a > sets_b else team_b_id
            
            cursor.execute('''
                UPDATE matches 
                SET score_a = ?, score_b = ?, 
                    set1_a = ?, set1_b = ?, set2_a = ?, set2_b = ?, set3_a = ?, set3_b = ?,
                    winner_team_id = ?
                WHERE match_id = ?
            ''', (sets_a, sets_b, s1a, s1b, s2a, s2b, s3a, s3b, winner_id, match_id))
            conn.commit()
            print(f"✅ Đã lưu BO3 trận {match_id}: Đội {team_a_id} ({sets_a}) - ({sets_b}) Đội {team_b_id}")
        except Exception as e:
            print(f"❌ Lỗi cập nhật điểm BO3: {e}")
        finally:
            conn.close()     

    # ==========================================
    # TẠO LỊCH THI ĐẤU (VÒNG BẢNG & KNOCKOUT)
    # ==========================================
    def generate_group_stage(self, tournament_id):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM matches WHERE tournament_id = ?", (tournament_id,))
        
        cursor.execute('SELECT team_id FROM teams')
        teams = [row[0] for row in cursor.fetchall()]
        
        if len(teams) < 4:
            print("❌ Cảnh báo: Không đủ 4 đội để chia bảng!")
            conn.close()
            return

        import random
        random.shuffle(teams)
        mid = len(teams) // 2
        group_a = teams[:mid]
        group_b = teams[mid:]

        matches = []
        for i in range(len(group_a)):
            for j in range(i + 1, len(group_a)):
                matches.append((tournament_id, group_a[i], group_a[j], 'Bảng A'))
                
        for i in range(len(group_b)):
            for j in range(i + 1, len(group_b)):
                matches.append((tournament_id, group_b[i], group_b[j], 'Bảng B'))

        cursor.executemany('INSERT INTO matches (tournament_id, team_a_id, team_b_id, stage) VALUES (?, ?, ?, ?)', matches)
        conn.commit()
        
        cursor.execute('SELECT count(*) FROM matches WHERE tournament_id = ?', (tournament_id,))
        print(f"✅ BÁO CÁO NHANH: Đã lưu thành công {cursor.fetchone()[0]} trận vòng bảng!")
        conn.close()

    def generate_round_robin(self, tournament_id):
        conn = self.db.connect()
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

    def generate_semi_finals_group(self, tournament_id):
        print("\n--- [HỆ THỐNG] ĐÃ NHẬN LỆNH CHỐT BÁN KẾT ---")
        conn = self.db.connect()
        cursor = conn.cursor()
        try:
            def get_top_2(stage_name):
                cursor.execute('''
                    SELECT team_a_id, team_b_id, winner_team_id 
                    FROM matches 
                    WHERE stage = ? AND tournament_id = ?
                ''', (stage_name, tournament_id))
                matches = cursor.fetchall()
                
                scores = {}
                for team_a, team_b, winner in matches:
                    if team_a not in scores: scores[team_a] = 0
                    if team_b not in scores: scores[team_b] = 0
                    if winner: scores[winner] = scores.get(winner, 0) + 1
                
                return sorted(scores.keys(), key=lambda t: scores[t], reverse=True)

            top_a = get_top_2('Bảng A')
            top_b = get_top_2('Bảng B')

            if len(top_a) < 2 or len(top_b) < 2:
                print("❌ LỖI: Mỗi bảng phải có ít nhất 2 đội đã đá và có kết quả!")
                return

            cursor.execute("DELETE FROM matches WHERE stage IN ('Bán kết 1', 'Bán kết 2') AND tournament_id = ?", (tournament_id,))

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
        conn = self.db.connect()
        cursor = conn.cursor()
        try:
            # Đã fix lỗi lấy nhầm trận bằng ORDER BY
            cursor.execute('''
                SELECT team_a_id, team_b_id, winner_team_id 
                FROM matches 
                WHERE tournament_id = ? 
                AND stage IN ('Bán kết 1', 'Bán kết 2') 
                AND winner_team_id IS NOT NULL 
                AND winner_team_id != ''
                ORDER BY match_id ASC
            ''', (tournament_id,))
            semis = cursor.fetchall()
            
            if len(semis) >= 2:
                s1, s2 = semis[-2], semis[-1]
                team_a_1, team_b_1, win_1 = str(s1[0]), str(s1[1]), str(s1[2])
                team_a_2, team_b_2, win_2 = str(s2[0]), str(s2[1]), str(s2[2])

                loser1 = team_a_1 if win_1 == team_b_1 else team_b_1
                loser2 = team_a_2 if win_2 == team_b_2 else team_b_2
                
                cursor.execute('DELETE FROM matches WHERE tournament_id = ? AND stage = ?', (tournament_id, 'Tranh hạng 3'))
                cursor.execute('''
                    INSERT INTO matches (tournament_id, team_a_id, team_b_id, stage)
                    VALUES (?, ?, ?, 'Tranh hạng 3')
                ''', (tournament_id, loser1, loser2))
                conn.commit()
                print(f"✅ Đã chốt Tranh hạng 3: {loser1} vs {loser2}")
        except Exception as e:
            print(f"❌ Lỗi tạo Tranh hạng 3: {e}")
        finally:
            conn.close()

    def generate_final_only(self, tournament_id):
        conn = self.db.connect()
        cursor = conn.cursor()
        try:
            # Đã fix lỗi lấy nhầm trận bằng ORDER BY
            cursor.execute('''
                SELECT winner_team_id 
                FROM matches 
                WHERE tournament_id = ? 
                AND stage IN ('Bán kết 1', 'Bán kết 2') 
                AND winner_team_id IS NOT NULL 
                AND winner_team_id != ''
                ORDER BY match_id ASC
            ''', (tournament_id,))
            winners = [str(row[0]) for row in cursor.fetchall()]
            
            if len(winners) >= 2:
                win1, win2 = winners[-2], winners[-1]
                
                cursor.execute('DELETE FROM matches WHERE tournament_id = ? AND stage = ?', (tournament_id, 'Chung kết'))
                cursor.execute('''
                    INSERT INTO matches (tournament_id, team_a_id, team_b_id, stage)
                    VALUES (?, ?, ?, 'Chung kết')
                ''', (tournament_id, win1, win2))
                conn.commit()
                print(f"✅ Đã chốt Chung kết: {win1} vs {win2}")
        except Exception as e:
            print(f"❌ Lỗi tạo Chung kết: {e}")
        finally:
            conn.close()