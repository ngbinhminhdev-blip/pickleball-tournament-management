from flask import Flask, render_template, request, redirect, url_for
from manager import TournamentManager

app = Flask(__name__)
manager = TournamentManager()

@app.route('/')
def home():
    all_players = manager.get_all_players()
    all_teams = manager.get_all_teams()
    all_tours = manager.get_all_tournaments() # Lấy thêm danh sách giải
    return render_template('index.html', players=all_players, teams=all_teams, tournaments=all_tours)

@app.route('/add_tournament', methods=['POST'])
def add_tournament():
    name = request.form.get('tour_name')
    if name:
        manager.create_tournament(name)
    return redirect(url_for('home'))

@app.route('/add_player', methods=['POST'])
def add_player():
    name = request.form.get('name')
    phone = request.form.get('phone') # Đổi chữ email thành phone
    gender = request.form.get('gender') 
    
    if name and phone and gender:
        manager.add_player(name, phone, gender) # Truyền phone vào hàm
        
    return redirect(url_for('home'))


@app.route('/add_team', methods=['POST'])
def add_team():
    p1_id = request.form.get('player1')
    p2_id = request.form.get('player2')
 
    if p1_id and p2_id and p1_id != p2_id:
        manager.create_team(int(p1_id), int(p2_id))
        
    return redirect(url_for('home'))


@app.route('/clear_teams')
def clear_teams():
    manager.clear_all_teams()
    return redirect(url_for('home'))

@app.route('/auto_pair_mixed')
def auto_pair_mixed():
    manager.auto_pair_mixed()
    return redirect(url_for('home'))

@app.route('/auto_pair_men')
def auto_pair_men():
    manager.auto_pair_same_gender('Nam')
    return redirect(url_for('home'))

@app.route('/auto_pair_women')
def auto_pair_women():
    manager.auto_pair_same_gender('Nữ')
    return redirect(url_for('home'))

@app.route('/tournament/<int:tour_id>')
def tournament(tour_id):
    matches = manager.get_matches(tour_id)
    group_a_teams = []
    group_b_teams = []
    
    for m in matches:
        if m[6] == 'Bảng A':
            group_a_teams.extend([m[1], m[2]]) 
        elif m[6] == 'Bảng B':
            group_b_teams.extend([m[1], m[2]])
            

    group_a = sorted(list(set(group_a_teams)))
    group_b = sorted(list(set(group_b_teams)))
    
    return render_template('tournament.html', 
                           matches=matches, 
                           tour_id=tour_id,
                           group_a=group_a,
                           group_b=group_b,
                           )

@app.route('/knockout/<int:tour_id>')
def knockout_stage(tour_id):
    all_matches = manager.get_matches(tour_id)
    knockout_matches = [m for m in all_matches if 'Bán kết' in m[6] or 'Chung kết' in m[6] or 'Tranh hạng 3' in m[6]]
    
    def is_valid(m):
        # m[3]=score_a, m[4]=score_b, m[5]=winner_team_id
        if m[5] is not None and (m[3] is None or m[4] is None):
            return False  
        return True
    
    knockout_matches = [m for m in knockout_matches if is_valid(m)]
    knockout_matches = [
        m if (m[3] is not None and m[4] is not None) else (m[0], m[1], m[2], None, None, None, m[6])
        for m in knockout_matches
    ]
    
    return render_template('knockout.html', matches=knockout_matches, tour_id=tour_id)

@app.route('/update_score', methods=['POST'])
def update_score():
    match_id = request.form.get('match_id', type=int)
    tour_id = request.form.get('tour_id')
    stage = request.form.get('stage')

    if stage in ['Bán kết 1', 'Bán kết 2', 'Chung kết', 'Tranh hạng 3']:
        s1a = request.form.get('set1_a', type=int)
        s1b = request.form.get('set1_b', type=int)
        s2a = request.form.get('set2_a', type=int)
        s2b = request.form.get('set2_b', type=int)
        s3a = request.form.get('set3_a', type=int) 
        s3b = request.form.get('set3_b', type=int) 

        if None in (s1a, s1b, s2a, s2b):
            return redirect(url_for('knockout_stage', tour_id=tour_id))

        win_sets_a = 0
        win_sets_b = 0

        if s1a > s1b: win_sets_a += 1
        else: win_sets_b += 1

        if s2a > s2b: win_sets_a += 1
        else: win_sets_b += 1

        if s3a is not None and s3b is not None and (s3a > 0 or s3b > 0):
            if s3a > s3b: win_sets_a += 1
            elif s3b > s3a: win_sets_b += 1

        if match_id and win_sets_a != win_sets_b:
            manager.update_score(match_id, win_sets_a, win_sets_b)

        return redirect(url_for('knockout_stage', tour_id=tour_id))

    else:
        score_a = request.form.get('score_a', type=int)
        score_b = request.form.get('score_b', type=int)

        if match_id and score_a is not None and score_b is not None:
            manager.update_score(match_id, score_a, score_b)

        return redirect(url_for('tournament', tour_id=tour_id))

@app.route('/gen_group/<int:tour_id>')
def gen_group(tour_id):
    print(f"📢 ALO ALO! ĐÃ BẤM NÚT TẠO BẢNG CHO GIẢI {tour_id}")
    manager.generate_group_stage(tour_id)
    return redirect(url_for('tournament', tour_id=tour_id))

@app.route('/gen_semi_group/<int:tour_id>')
def gen_semi_group(tour_id):
    manager.generate_semi_finals_group(tour_id)
    return redirect(url_for('knockout_stage', tour_id=tour_id))


@app.route('/gen_rr/<int:tour_id>')
def gen_rr(tour_id):
    manager.generate_round_robin(tour_id)
    return redirect(url_for('tournament', tour_id=tour_id))

@app.route('/gen_semi_rr/<int:tour_id>')
def gen_semi_rr(tour_id):
    manager.generate_semi_finals_rr(tour_id)
    return redirect(url_for('tournament', tour_id=tour_id))

@app.route('/generate_third_place/<int:tour_id>')
def generate_third_place_route(tour_id):
    manager.generate_third_place(tour_id)
   
    return redirect(f'/knockout/{tour_id}')

@app.route('/generate_final_only/<int:tour_id>')
def generate_final_only_route(tour_id):
    manager.generate_final_only(tour_id)
    return redirect(f'/knockout/{tour_id}')


@app.route('/delete_this_tour/<int:tour_id>')
def delete_tour_final(tour_id):
    try:
        manager.delete_tournament(tour_id)
    except Exception as e:
        print(f"Lỗi: {e}") 
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)