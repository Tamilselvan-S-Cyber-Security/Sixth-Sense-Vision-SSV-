import os
import sqlite3
from datetime import datetime

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('security_system.db')
        self.create_tables()

    def create_tables(self):
        with self.conn as conn:
            # Users table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Vehicle records table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS vehicle_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    plate_number TEXT NOT NULL,
                    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    owner_name TEXT,
                    vehicle_type TEXT,
                    notes TEXT
                )
            """)

    def add_user(self, username, password_hash):
        with self.conn as conn:
            cur = conn.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, password_hash)
            )
            return cur.lastrowid

    def get_user(self, username):
        with self.conn as conn:
            cur = conn.execute("SELECT * FROM users WHERE username = ?", (username,))
            row = cur.fetchone()
            if row:
                return {
                    'id': row[0],
                    'username': row[1],
                    'password_hash': row[2],
                    'created_at': row[3]
                }
            return None

    def add_vehicle_record(self, plate_number, owner_name=None, vehicle_type=None, notes=None):
        with self.conn as conn:
            cur = conn.execute("""
                INSERT INTO vehicle_records 
                (plate_number, owner_name, vehicle_type, notes)
                VALUES (?, ?, ?, ?)
            """, (plate_number, owner_name, vehicle_type, notes))
            return cur.lastrowid

    def search_vehicle_records(self, search_term, search_type="plate_number"):
        """Search vehicle records by different criteria"""
        with self.conn as conn:
            if search_type == "Owner Name":
                query = """
                    SELECT * FROM vehicle_records 
                    WHERE owner_name LIKE ? 
                    ORDER BY detected_at DESC
                """
            elif search_type == "Vehicle Type":
                query = """
                    SELECT * FROM vehicle_records 
                    WHERE vehicle_type LIKE ? 
                    ORDER BY detected_at DESC
                """
            else:  # Default to plate number search
                query = """
                    SELECT * FROM vehicle_records 
                    WHERE plate_number LIKE ? 
                    ORDER BY detected_at DESC
                """

            cur = conn.execute(query, (f'%{search_term}%',))
            rows = cur.fetchall()
            return [{
                'id': row[0],
                'plate_number': row[1],
                'detected_at': row[2],
                'owner_name': row[3],
                'vehicle_type': row[4],
                'notes': row[5]
            } for row in rows]