# database.py
import sqlite3
import json
from datetime import datetime

class ProjectDatabase:
    def __init__(self, db_path='projects.db'):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.create_tables()
    
    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                author TEXT,
                description TEXT,
                genre TEXT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP,
                metadata TEXT
            )
        ''')
        # Add more tables for characters, scenes, assets
        self.conn.commit()