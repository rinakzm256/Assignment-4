import time

class AIServiceClient:
    def __init__(self, simulate_timeout=False, timeout_seconds=2.0):
        self.simulate_timeout = simulate_timeout
        self.timeout_seconds = timeout_seconds

    def suggest_category(self, note_text: str) -> tuple[str, bool]:
        """
        Returns (suggested_category, is_ai_available).
        If API takes > 2s or fails, defaults to 'General/Other' (AIR-02 / NFR-02).
        """
        if self.simulate_timeout:
            time.sleep(2.5)  # Triggers timeout threshold
            return "General/Other", False

        # Rule-based simulated AI processing within threshold
        text_lower = note_text.lower()
        if any(w in text_lower for w in ["cough", "breathing", "fever", "lungs"]):
            category = "Respiratory"
        elif any(w in text_lower for w in ["stomach", "nausea", "vomiting", "digest"]):
            category = "Digestive"
        elif any(w in text_lower for w in ["joint", "bone", "muscle", "fracture", "pain"]):
            category = "Musculoskeletal"
        else:
            category = "General/Other"

        return category, True