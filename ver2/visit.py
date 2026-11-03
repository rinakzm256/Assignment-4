from datetime import datetime

class VisitNote:
    def __init__(self, visit_id, patient_id, timestamp, clinician_id, note_body, category=None):
        self.visit_id = visit_id
        self.patient_id = patient_id
        self.timestamp = timestamp
        self.clinician_id = clinician_id
        self.note_body = note_body
        self.category = category

class VisitManager:
    def __init__(self, db_manager):
        self.db = db_manager

    def add_visit_note(self, patient_id, clinician_id, note_body, category=None):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO visit_notes (patient_id, timestamp, clinician_id, note_body, category)
                VALUES (?, ?, ?, ?, ?)
                """,
                (patient_id, timestamp, clinician_id, note_body, category)
            )
            visit_id = cursor.lastrowid
        return VisitNote(visit_id, patient_id, timestamp, clinician_id, note_body, category)

    def get_patient_history(self, patient_id):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM visit_notes WHERE patient_id = ? ORDER BY timestamp DESC",
                (patient_id,)
            )
            rows = cursor.fetchall()
        return [
            VisitNote(
                row["visit_id"],
                row["patient_id"],
                row["timestamp"],
                row["clinician_id"],
                row["note_body"],
                row["category"]
            )
            for row in rows
        ]