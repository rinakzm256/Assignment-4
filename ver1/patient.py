import uuid
from persistence import DatabaseManager

class Patient:
    def __init__(self, patient_id: str, name: str, dob: str, phone: str = "", address: str = ""):
        # V1 Weakness: Attribute is public and mutable
        self.patient_id = patient_id
        self.name = name
        self.dob = dob
        self.phone = phone
        self.address = address

class PatientManager:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def generate_patient_id(self) -> str:
        # Alphanumeric unique hash ID prefix
        return f"P-{uuid.uuid4().hex[:8].upper()}"

    def register_patient(self, name: str, dob: str, phone: str, address: str) -> Patient:
        patient_id = self.generate_patient_id()
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO patients VALUES (?, ?, ?, ?, ?)",
            (patient_id, name, dob, phone, address)
        )
        conn.commit()
        conn.close()
        return Patient(patient_id, name, dob, phone, address)

    def search_patient(self, query: str):
        """Search by exact Patient ID or partial name (FR-03)."""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Check exact ID first
        cursor.execute("SELECT * FROM patients WHERE patient_id = ?", (query.strip(),))
        record = cursor.fetchone()
        
        if not record:
            # Try partial name search
            cursor.execute("SELECT * FROM patients WHERE name LIKE ?", (f"%{query.strip()}%",))
            record = cursor.fetchone()

        conn.close()
        if record:
            return Patient(patient_id=record[0], name=record[1], dob=record[2], phone=record[3], address=record[4])
        return None

    def update_permitted_demographics(self, patient_id: str, name: str, dob: str, phone: str, address: str) -> bool:
        """Update allowed fields while keeping Patient ID locked (FR-04)."""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE patients SET name = ?, dob = ?, phone = ?, address = ? WHERE patient_id = ?",
            (name, dob, phone, address, patient_id)
        )
        conn.commit()
        conn.close()
        return True