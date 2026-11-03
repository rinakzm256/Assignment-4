import sqlite3
from contextlib import contextmanager

class DatabaseManager:
    def __init__(self, db_path="prs.db"):
        self.db_path = db_path
        self._init_db()

    @contextmanager
    def get_connection(self):
        """Context manager guaranteeing connection closure and transaction safety."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS patients (
                    patient_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    dob TEXT NOT NULL,
                    gender TEXT NOT NULL,
                    contact_info TEXT NOT NULL,
                    address TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS visit_notes (
                    visit_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    clinician_id TEXT NOT NULL,
                    note_body TEXT NOT NULL,
                    category TEXT,
                    FOREIGN KEY (patient_id) REFERENCES patients (patient_id)
                )
            """)