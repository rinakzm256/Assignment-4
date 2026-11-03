import datetime
from persistence import DatabaseManager
from ai_integration import AIServiceClient

class VisitNote:
    def __init__(self, note_id: int, patient_id: str, date_time: str, clinician_id: str, note_text: str, category: str):
        self.note_id = note_id
        self.patient_id = patient_id
        self.date_time = date_time
        self.clinician_id = clinician_id
        self.note_text = note_text
        self.category = category

class VisitManager:
    def __init__(self, db: DatabaseManager, ai_client: AIServiceClient):
        self.db = db
        self.ai_client = ai_client

    def request_ai_category(self, note_text: str) -> tuple[str, bool]:
        return self.ai_client.suggest_category(note_text)

    def add_visit_note(self, patient_id: str, clinician_id: str, note_text: str, category: str) -> bool:
        # Check patient existence (Rule 2)
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT patient_id FROM patients WHERE patient_id = ?", (patient_id,))
        if not cursor.fetchone():
            conn.close()
            raise ValueError("Cannot add visit note: Patient ID does not exist.")

        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO visit_notes (patient_id, date_time, clinician_id, note_text, category) VALUES (?, ?, ?, ?, ?)",
            (patient_id, clinician_id, note_text, category)
        )
        conn.commit()
        conn.close()
        return True

    def get_patient_history(self, patient_id: str) -> list[VisitNote]:
        """Fetch history in reverse chronological order (FR-06)."""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, patient_id, date_time, clinician_id, note_text, category FROM visit_notes WHERE patient_id = ? ORDER BY id DESC",
            (patient_id,)
        )
        rows = cursor.fetchall()
        conn.close()
        
        return [VisitNote(r[0], r[1], r[2], r[3], r[4], r[5]) for r in rows]