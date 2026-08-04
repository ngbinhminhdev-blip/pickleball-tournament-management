import sqlite3

class DatabaseHelper:
    def __init__(self, db_path='pickleball.db'):
        self.db_path = db_path

    def connect(self):
        """Trả về connection đến database"""
        return sqlite3.connect(self.db_path)