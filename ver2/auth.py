class AuthService:
    def __init__(self):
        self.current_user = None

    def login(self, username, role):
        self.current_user = {"username": username, "role": role.lower()}
        return True

    def logout(self):
        self.current_user = None

    def is_authenticated(self):
        return self.current_user is not None

    def get_role(self):
        return self.current_user["role"] if self.current_user else None

    def can_register_patient(self):
        """Decouples permission checking from GUI logic."""
        return self.get_role() in ["admin", "superadmin"]

    def can_add_visit_note(self):
        """Decouples permission checking from GUI logic."""
        return self.get_role() in ["clinical", "doctor", "nurse"]
    
    def can_update_patient(self):
      """Permission check for editing patient demographics."""
      return self.get_role() in ["admin", "superadmin"]