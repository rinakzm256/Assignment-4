import uuid

class Patient:
    def __init__(self, patient_id, name, dob, gender, contact_info, address=None):
        self._patient_id = patient_id  # Private attribute for immutability
        self.name = name
        self.dob = dob
        self.gender = gender
        self.contact_info = contact_info
        self.address = address

    @property
    def patient_id(self):
        """Read-only property enforcing immutable patient_id."""
        return self._patient_id

    def to_dict(self):
        return {
            "patient_id": self.patient_id,
            "name": self.name,
            "dob": self.dob,
            "gender": self.gender,
            "contact_info": self.contact_info,
            "address": self.address
        }

class PatientManager:
    def __init__(self, db_manager):
        self.db = db_manager

    def generate_patient_id(self):
        return f"P-{uuid.uuid4().hex[:8].upper()}"

    def register_patient(self, name, dob, gender, contact_info, address=None):
        patient_id = self.generate_patient_id()
        patient = Patient(patient_id, name, dob, gender, contact_info, address)
        
        with self.db.get_connection() as conn:
            conn.cursor().execute(
                """
                INSERT INTO patients (patient_id, name, dob, gender, contact_info, address)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (patient.patient_id, patient.name, patient.dob, patient.gender, patient.contact_info, patient.address)
            )
        return patient

    def search_patient(self, query):
        """Combined single SQL query optimization for ID and name matching."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            search_param = f"%{query}%"
            cursor.execute(
                """
                SELECT * FROM patients 
                WHERE patient_id = ? OR name LIKE ?
                """,
                (query, search_param)
            )
            rows = cursor.fetchall()
            
        return [
            Patient(
                row["patient_id"],
                row["name"],
                row["dob"],
                row["gender"],
                row["contact_info"],
                row["address"]
            )
            for row in rows
        ]
    def update_patient(
        self, patient_id, name, dob, gender, contact_info, address=None
    ):
      """Updates existing patient demographic details in the database."""
      with self.db.get_connection() as conn:
        conn.cursor().execute(
            """
                UPDATE patients 
                SET name = ?, dob = ?, gender = ?, contact_info = ?, address = ?
                WHERE patient_id = ?
                """,
            (name, dob, gender, contact_info, address, patient_id),
        )
      return True