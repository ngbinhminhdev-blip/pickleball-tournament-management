import sqlite3


def upgrade_database():
    conn = sqlite3.connect("pickleball.db")
    cursor = conn.cursor()

    # Add Best-of-3 match score columns
    score_columns = [
        "set1_a",
        "set1_b",
        "set2_a",
        "set2_b",
        "set3_a",
        "set3_b",
    ]

    for column in score_columns:
        try:
            cursor.execute(
                f"ALTER TABLE matches ADD COLUMN {column} INTEGER DEFAULT 0"
            )
            print(f"Added column: {column}")
        except sqlite3.OperationalError:
            print(f"Column '{column}' already exists.")

    # Add tournament ID column
    try:
        cursor.execute(
            "ALTER TABLE matches ADD COLUMN tournament_id INTEGER DEFAULT 1"
        )
        print("Added column: tournament_id")
    except sqlite3.OperationalError:
        print("Column 'tournament_id' already exists.")

    # Create tournament_players table
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tournament_players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tournament_id INTEGER NOT NULL,
                player_id INTEGER NOT NULL,
                UNIQUE(tournament_id, player_id)
            )
        """)
        print("Created table: tournament_players")
    except Exception as e:
        print(f"Error: {e}")

    conn.commit()
    conn.close()

    print("Database upgrade completed successfully.")


if __name__ == "__main__":
    upgrade_database()