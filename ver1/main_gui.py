import tkinter as tk
from tkinter import messagebox, ttk

from persistence import DatabaseManager
from auth import User, AuthService
from patient import PatientManager
from ai_integration import AIServiceClient
from visit import VisitManager

class PRSApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PRS - Patient Record System (V1)")
        self.root.geometry("750x650")

        # Initialize Services
        self.db = DatabaseManager()
        self.patient_mgr = PatientManager(self.db)
        self.ai_client = AIServiceClient()
        self.visit_mgr = VisitManager(self.db, self.ai_client)

        # Active Session State
        self.current_user = User(username="staff1", role="Admin")
        self.active_patient = None

        self._build_ui()

    def _build_ui(self):
        # Role Selection Header
        top_frame = tk.Frame(self.root, bd=1, relief=tk.RAISED, bg="#f0f0f0")
        top_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(top_frame, text="Active User Role:", bg="#f0f0f0").pack(side=tk.LEFT, padx=5)
        self.role_var = tk.StringVar(value=self.current_user.role)
        role_combo = ttk.Combobox(top_frame, textvariable=self.role_var, values=["Admin", "Clinical Staff"], state="readonly", width=15)
        role_combo.pack(side=tk.LEFT, padx=5)
        role_combo.bind("<<ComboboxSelected>>", self._on_role_change)

        # Tabs Setup
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.tab_search = ttk.Frame(self.notebook)
        self.tab_register = ttk.Frame(self.notebook)
        self.tab_visit = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_search, text="Search & View Patient")
        self.notebook.add(self.tab_register, text="Register New Patient")
        self.notebook.add(self.tab_visit, text="Visit Notes & History")

        self._setup_search_tab()
        self._setup_register_tab()
        self._setup_visit_tab()

    def _on_role_change(self, event):
        self.current_user.role = self.role_var.get()
        messagebox.showinfo("Role Switch", f"Switched active role to: {self.current_user.role}")

    # --- TAB 1: SEARCH & UPDATE ---
    def _setup_search_tab(self):
        frame = tk.LabelFrame(self.tab_search, text="Patient Lookup")
        frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(frame, text="Search (ID or Name):").grid(row=0, column=0, padx=5, pady=5)
        self.ent_search_query = tk.Entry(frame, width=30)
        self.ent_search_query.grid(row=0, column=1, padx=5, pady=5)
        
        btn_search = tk.Button(frame, text="Search", command=self._handle_search)
        btn_search.grid(row=0, column=2, padx=5, pady=5)

        # Patient Info Display / Editing
        details_frame = tk.LabelFrame(self.tab_search, text="Patient Details")
        details_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Label(details_frame, text="Patient ID:").grid(row=0, column=0, sticky="e")
        self.lbl_pid = tk.Label(details_frame, text="-", font=("Arial", 10, "bold"))
        self.lbl_pid.grid(row=0, column=1, sticky="w")

        tk.Label(details_frame, text="Full Name:").grid(row=1, column=0, sticky="e")
        self.ent_name = tk.Entry(details_frame, width=30)
        self.ent_name.grid(row=1, column=1, sticky="w")

        tk.Label(details_frame, text="DOB (YYYY-MM-DD):").grid(row=2, column=0, sticky="e")
        self.ent_dob = tk.Entry(details_frame, width=30)
        self.ent_dob.grid(row=2, column=1, sticky="w")

        tk.Label(details_frame, text="Phone:").grid(row=3, column=0, sticky="e")
        self.ent_phone = tk.Entry(details_frame, width=30)
        self.ent_phone.grid(row=3, column=1, sticky="w")

        tk.Label(details_frame, text="Address:").grid(row=4, column=0, sticky="e")
        self.ent_address = tk.Entry(details_frame, width=30)
        self.ent_address.grid(row=4, column=1, sticky="w")

        btn_save_demo = tk.Button(details_frame, text="Update Permitted Demographics", command=self._handle_update_demographics)
        btn_save_demo.grid(row=5, column=1, pady=10, sticky="w")

    def _handle_search(self):
        query = self.ent_search_query.get().strip()
        if not query:
            return

        patient = self.patient_mgr.search_patient(query)
        if not patient:
            # Explicit scenario handling per Assignment #3 Sequence Diagram
            res = messagebox.askyesno("Patient ID Not Found", "No patient record found. Would you like to register a new patient?")
            if res:
                self.notebook.select(self.tab_register)
            return

        self.active_patient = patient
        self.lbl_pid.config(text=patient.patient_id)
        
        self.ent_name.delete(0, tk.END); self.ent_name.insert(0, patient.name)
        self.ent_dob.delete(0, tk.END); self.ent_dob.insert(0, patient.dob)
        self.ent_phone.delete(0, tk.END); self.ent_phone.insert(0, patient.phone)
        self.ent_address.delete(0, tk.END); self.ent_address.insert(0, patient.address)

    def _handle_update_demographics(self):
        if not AuthService.is_admin(self.current_user):
            messagebox.showerror("Permission Error", "Access Denied: Only Admin staff can edit demographics.")
            return

        if not self.active_patient:
            messagebox.showwarning("Warning", "No active patient selected.")
            return

        self.patient_mgr.update_permitted_demographics(
            self.active_patient.patient_id,
            self.ent_name.get().strip(),
            self.ent_dob.get().strip(),
            self.ent_phone.get().strip(),
            self.ent_address.get().strip()
        )
        messagebox.showinfo("Success", "Demographics updated successfully!")

    # --- TAB 2: REGISTER ---
    def _setup_register_tab(self):
        frame = tk.LabelFrame(self.tab_register, text="New Patient Intake")
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Label(frame, text="Full Name*:").grid(row=0, column=0, sticky="e", pady=5)
        ent_reg_name = tk.Entry(frame, width=30); ent_reg_name.grid(row=0, column=1, sticky="w", pady=5)

        tk.Label(frame, text="DOB (YYYY-MM-DD)*:").grid(row=1, column=0, sticky="e", pady=5)
        ent_reg_dob = tk.Entry(frame, width=30); ent_reg_dob.grid(row=1, column=1, sticky="w", pady=5)

        tk.Label(frame, text="Phone:").grid(row=2, column=0, sticky="e", pady=5)
        ent_reg_phone = tk.Entry(frame, width=30); ent_reg_phone.grid(row=2, column=1, sticky="w", pady=5)

        tk.Label(frame, text="Address:").grid(row=3, column=0, sticky="e", pady=5)
        ent_reg_address = tk.Entry(frame, width=30); ent_reg_address.grid(row=3, column=1, sticky="w", pady=5)

        def submit_registration():
            if not AuthService.is_admin(self.current_user):
                messagebox.showerror("Permission Error", "Access Denied: Only Admin staff can register patients.")
                return

            name = ent_reg_name.get().strip()
            dob = ent_reg_dob.get().strip()
            if not name or not dob:
                messagebox.showwarning("Input Error", "Name and DOB are required fields.")
                return

            p = self.patient_mgr.register_patient(name, dob, ent_reg_phone.get().strip(), ent_reg_address.get().strip())
            messagebox.showinfo("Success", f"Patient Created!\nGenerated ID: {p.patient_id}")
            ent_reg_name.delete(0, tk.END); ent_reg_dob.delete(0, tk.END)
            ent_reg_phone.delete(0, tk.END); ent_reg_address.delete(0, tk.END)

        tk.Button(frame, text="Generate ID & Create Record", command=submit_registration).grid(row=4, column=1, pady=15, sticky="w")

    # --- TAB 3: VISIT NOTES & HISTORY ---
    def _setup_visit_tab(self):
        top_frame = tk.Frame(self.tab_visit)
        top_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Note Entry Box
        tk.Label(top_frame, text="Clinical Visit Note Description:").pack(anchor="w")
        self.txt_note = tk.Text(top_frame, height=5, width=60)
        self.txt_note.pack(fill=tk.X, pady=5)

        ai_bar = tk.Frame(top_frame)
        ai_bar.pack(fill=tk.X, pady=5)

        btn_ai = tk.Button(ai_bar, text="Get AI Category Suggestion", command=self._get_ai_suggestion)
        btn_ai.pack(side=tk.LEFT, padx=5)

        tk.Label(ai_bar, text="Category:").pack(side=tk.LEFT, padx=5)
        self.category_var = tk.StringVar(value="General/Other")
        categories = ["Respiratory", "Digestive", "Musculoskeletal", "General/Other"]
        self.cmb_category = ttk.Combobox(ai_bar, textvariable=self.category_var, values=categories, width=18)
        self.cmb_category.pack(side=tk.LEFT, padx=5)

        # Timeout simulator check button
        self.chk_timeout_var = tk.BooleanVar(value=False)
        tk.Checkbutton(ai_bar, text="Simulate AI Timeout (>2s)", variable=self.chk_timeout_var, command=self._toggle_ai_timeout).pack(side=tk.RIGHT, padx=5)

        btn_save_note = tk.Button(top_frame, text="Save Visit Note", command=self._save_visit_note, bg="#e1f5fe")
        btn_save_note.pack(anchor="w", pady=5)

        # History Display
        tk.Label(top_frame, text="Patient Visit History (Reverse Chronological):").pack(anchor="w", pady=(10, 0))
        self.txt_history = tk.Text(top_frame, height=10, width=60, state="disabled")
        self.txt_history.pack(fill=tk.BOTH, expand=True, pady=5)

    def _toggle_ai_timeout(self):
        self.ai_client.simulate_timeout = self.chk_timeout_var.get()

    def _get_ai_suggestion(self):
        note = self.txt_note.get("1.0", tk.END).strip()
        if not note:
            messagebox.showwarning("Warning", "Please enter visit note text first.")
            return

        cat, success = self.visit_mgr.request_ai_category(note)
        self.category_var.set(cat)
        if not success:
            messagebox.showwarning("AI Service Warning", "AI service timed out (>2s). Defaulting category to 'General/Other'. Note can still be saved.")

    def _save_visit_note(self):
        if not AuthService.is_clinical(self.current_user):
            messagebox.showerror("Permission Error", "Access Denied: Only Clinical Staff can enter visit notes.")
            return

        if not self.active_patient:
            messagebox.showwarning("Warning", "No active patient selected. Search for a patient first.")
            return

        note = self.txt_note.get("1.0", tk.END).strip()
        if not note:
            messagebox.showwarning("Warning", "Visit note description cannot be empty.")
            return

        cat = self.category_var.get()
        self.visit_mgr.add_visit_note(self.active_patient.patient_id, self.current_user.username, note, cat)
        messagebox.showinfo("Success", "Visit note saved!")
        self.txt_note.delete("1.0", tk.END)
        self._refresh_history()

    def _refresh_history(self):
        if not self.active_patient:
            return
        notes = self.visit_mgr.get_patient_history(self.active_patient.patient_id)
        
        self.txt_history.config(state="normal")
        self.txt_history.delete("1.0", tk.END)
        for n in notes:
            entry = f"[{n.date_time}] | Clinician: {n.clinician_id} | Category: {n.category}\nNote: {n.note_text}\n{'-'*60}\n"
            self.txt_history.insert(tk.END, entry)
        self.txt_history.config(state="disabled")

if __name__ == "__main__":
    root = tk.Tk()
    app = PRSApp(root)
    root.mainloop()