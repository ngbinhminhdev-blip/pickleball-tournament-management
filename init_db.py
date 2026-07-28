import sqlite3

def init_db():
    conn = sqlite3.connect('pickleball.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
            player_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT UNIQUE NOT NULL,
            gender TEXT NOT NULL,
            elo_rating INTEGER DEFAULT 1200
        )
    ''')


    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teams (
            team_id INTEGER PRIMARY KEY AUTOINCREMENT,
            player1_id INTEGER,
            player2_id INTEGER,
            FOREIGN KEY (player1_id) REFERENCES players(player_id),
            FOREIGN KEY (player2_id) REFERENCES players(player_id)
        )
    ''')
 
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tournaments (
            tournament_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS matches (
            match_id INTEGER PRIMARY KEY AUTOINCREMENT,
            tournament_id INTEGER,
            team_a_id INTEGER,
            team_b_id INTEGER,
            score_a INTEGER,
            score_b INTEGER,
            winner_team_id INTEGER,
            stage TEXT,
            FOREIGN KEY (tournament_id) REFERENCES tournaments(tournament_id),
            FOREIGN KEY (team_a_id) REFERENCES teams(team_id),
            FOREIGN KEY (team_b_id) REFERENCES teams(team_id)
        )
    ''')

    conn.commit()
    conn.close()
    print("✅ Create successfully data pickleball.db!")

    cursor.execute(
    "DELETE FROM matches WHERE stage IN ('Bán kết 1', 'Bán kết 2') AND tournament_id = ?",
    (tournament_id,)
    )
    conn.commit()  

if __name__ == '__main__':
    init_db()