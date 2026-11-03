import time

class AIServiceClient:
    def __init__(self, timeout=5):
        self.timeout = timeout

    def suggest_category(self, note_text, simulate_timeout=False):
        """Simulates REST call to analyze text and return a category."""
        if simulate_timeout:
            return "General/Other (Timeout Fallback)"

        text_lower = note_text.lower()
        if "cardio" in text_lower or "heart" in text_lower or "bp" in text_lower:
            return "Cardiology"
        elif "fever" in text_lower or "cough" in text_lower or "flu" in text_lower:
            return "General Practice"
        elif "bone" in text_lower or "joint" in text_lower or "fracture" in text_lower:
            return "Orthopedics"
        return "General/Other"