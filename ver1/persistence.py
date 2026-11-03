import sqlite3

DB_FILE = "prs_v1.db"

class DatabaseManager:
    def __init__(self, db_path=DB_FILE):
        self.db_path = db_path
        self._init_db()

    def get_connection(self):
        # Note: V1 opens raw connections without context manager wrappers
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patients (
                patient_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                dob TEXT NOT NULL,
                phone TEXT,
                address TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS visit_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id TEXT NOT NULL,
                date_time TEXT NOT NULL,
                clinician_id TEXT NOT NULL,
                note_text TEXT NOT NULL,
                category TEXT NOT NULL,
                FOREIGN KEY (patient_id) REFERENCES patients (patient_id)
            )
        ''')
        conn.commit()
        conn.close()