class User:
    def __init__(self, username: str, role: str):
        self.username = username
        self.role = role  # "Admin" or "Clinical Staff"

class AuthService:
    @staticmethod
    def is_admin(user: User) -> bool:
        return user.role == "Admin"

    @staticmethod
    def is_clinical(user: User) -> bool:
        return user.role == "Clinical Staff"