import tkinter as tk
from tkinter import messagebox, ttk

from ai_integration import AIServiceClient
from auth import AuthService
from patient import PatientManager
from persistence import DatabaseManager
from visit import VisitManager


class PRSApp:

  def __init__(
      self, root, auth_service, patient_manager, visit_manager, ai_client
  ):
    self.root = root
    self.auth = auth_service
    self.patient_mgr = patient_manager
    self.visit_mgr = visit_manager
    self.ai_client = ai_client

    self.root.title("Patient Record System (V2)")
    self.root.geometry("850x750")
    self._build_ui()

  def _build_ui(self):
    # Top Session Control Frame
    session_frame = ttk.Frame(self.root, padding="10")
    session_frame.pack(fill=tk.X)

    self.status_lbl = ttk.Label(
        session_frame, text="", font=("Arial", 10, "bold")
    )
    self.status_lbl.pack(side=tk.LEFT)

    ttk.Label(session_frame, text="Switch Role:").pack(
        side=tk.LEFT, padx=(20, 5)
    )
    self.role_combo = ttk.Combobox(
        session_frame,
        values=["Admin (admin_user)", "Clinical (dr_smith)", "Guest"],
        state="readonly",
        width=20,
    )
    self.role_combo.set("Admin (admin_user)")
    self.role_combo.pack(side=tk.LEFT, padx=5)
    self.role_combo.bind("<<ComboboxSelected>>", self._handle_role_change)

    # Main Notebook (Tabs)
    self.notebook = ttk.Notebook(self.root)
    self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    # Tab 1: Search
    self.tab_search = ttk.Frame(self.notebook, padding="10")
    self.notebook.add(self.tab_search, text="Search & View Patients")
    self._build_search_tab()

    # Tab 2: Register & Edit Demographics
    self.tab_register = ttk.Frame(self.notebook, padding="10")
    self.notebook.add(self.tab_register, text="Register / Edit Patient")
    self._build_register_tab()

    # Tab 3: Visit Notes
    self.tab_visits = ttk.Frame(self.notebook, padding="10")
    self.notebook.add(self.tab_visits, text="Visit Notes & AI")
    self._build_visits_tab()

    self._update_session_display()

  def _update_session_display(self):
    user = (
        self.auth.current_user["username"] if self.auth.current_user else "Guest"
    )
    role = self.auth.get_role() or "None"
    self.status_lbl.config(text=f"Logged in as: {user} ({role.upper()})")

  def _handle_role_change(self, event):
    selected = self.role_combo.get()
    if "Admin" in selected:
      self.auth.login("admin_user", "admin")
    elif "Clinical" in selected:
      self.auth.login("dr_smith", "clinical")
    else:
      self.auth.logout()
    self._update_session_display()

  # --- TAB 1: SEARCH ---

  def _build_search_tab(self):
    search_frame = ttk.LabelFrame(
        self.tab_search, text="Search Database", padding="5"
    )
    search_frame.pack(fill=tk.X, pady=5)

    self.search_entry = ttk.Entry(search_frame)
    self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

    search_btn = ttk.Button(
        search_frame, text="Search", command=self._handle_search
    )
    search_btn.pack(side=tk.LEFT, padx=5)

    self.results_box = tk.Text(self.tab_search, height=18, state=tk.DISABLED)
    self.results_box.pack(fill=tk.BOTH, expand=True, pady=5)

  def _handle_search(self):
    query = self.search_entry.get().strip()
    if not query:
      messagebox.showwarning("Warning", "Please enter a search query.")
      return
    results = self.patient_mgr.search_patient(query)
    self._display_search_results(results)

  def _display_search_results(self, results):
    self.results_box.config(state=tk.NORMAL)
    self.results_box.delete("1.0", tk.END)
    if not results:
      self.results_box.insert(tk.END, "No matching patient records found.\n")
    else:
      for p in results:
        display_str = (
            f"ID: {p.patient_id}\n"
            f"Name: {p.name}\n"
            f"DOB: {p.dob} | Gender: {p.gender}\n"
            f"Contact: {p.contact_info}\n"
            f"Address: {p.address or 'N/A'}\n"
            f"{'-'*50}\n"
        )
        self.results_box.insert(tk.END, display_str)
    self.results_box.config(state=tk.DISABLED)

  # --- TAB 2: REGISTER & UPDATE DEMOGRAPHICS ---

  def _build_register_tab(self):
    # Lookup Section for Updating Existing Patients
    lookup_frame = ttk.LabelFrame(
        self.tab_register, text="Edit Existing Patient", padding="10"
    )
    lookup_frame.pack(fill=tk.X, pady=5)

    ttk.Label(lookup_frame, text="Patient ID:").pack(side=tk.LEFT, padx=5)
    self.edit_pid_entry = ttk.Entry(lookup_frame, width=20)
    self.edit_pid_entry.pack(side=tk.LEFT, padx=5)

    load_btn = ttk.Button(
        lookup_frame,
        text="Load Details for Editing",
        command=self._handle_load_patient_for_edit,
    )
    load_btn.pack(side=tk.LEFT, padx=5)

    # Demographic Fields Form
    reg_frame = ttk.LabelFrame(
        self.tab_register, text="Patient Demographic Details", padding="10"
    )
    reg_frame.pack(fill=tk.X, pady=5)

    ttk.Label(reg_frame, text="Full Name:").grid(
        row=0, column=0, sticky=tk.W, pady=5
    )
    self.reg_name = ttk.Entry(reg_frame, width=40)
    self.reg_name.grid(row=0, column=1, sticky=tk.W, pady=5)

    ttk.Label(reg_frame, text="DOB (YYYY-MM-DD):").grid(
        row=1, column=0, sticky=tk.W, pady=5
    )
    self.reg_dob = ttk.Entry(reg_frame, width=40)
    self.reg_dob.grid(row=1, column=1, sticky=tk.W, pady=5)

    ttk.Label(reg_frame, text="Gender:").grid(
        row=2, column=0, sticky=tk.W, pady=5
    )
    self.reg_gender = ttk.Combobox(
        reg_frame,
        values=["Male", "Female", "Other"],
        state="readonly",
        width=38,
    )
    self.reg_gender.grid(row=2, column=1, sticky=tk.W, pady=5)

    ttk.Label(reg_frame, text="Contact Info:").grid(
        row=3, column=0, sticky=tk.W, pady=5
    )
    self.reg_contact = ttk.Entry(reg_frame, width=40)
    self.reg_contact.grid(row=3, column=1, sticky=tk.W, pady=5)

    ttk.Label(reg_frame, text="Address:").grid(
        row=4, column=0, sticky=tk.W, pady=5
    )
    self.reg_address = ttk.Entry(reg_frame, width=40)
    self.reg_address.grid(row=4, column=1, sticky=tk.W, pady=5)

    # Action Buttons
    btn_frame = ttk.Frame(self.tab_register)
    btn_frame.pack(anchor=tk.W, pady=10)

    reg_btn = ttk.Button(
        btn_frame,
        text="Register New Patient",
        command=self._handle_register_patient,
    )
    reg_btn.pack(side=tk.LEFT, padx=(0, 10))

    update_btn = ttk.Button(
        btn_frame,
        text="Update Selected Patient Info",
        command=self._handle_update_patient,
    )
    update_btn.pack(side=tk.LEFT)

  def _handle_load_patient_for_edit(self):
    pid = self.edit_pid_entry.get().strip()
    if not pid:
      messagebox.showwarning("Warning", "Please enter a Patient ID to load.")
      return

    results = self.patient_mgr.search_patient(pid)
    match = next((p for p in results if p.patient_id == pid), None)

    if not match:
      messagebox.showerror(
          "Not Found", f"No patient found matching ID: {pid}"
      )
      return

    # Populate fields for editing
    self.reg_name.delete(0, tk.END)
    self.reg_name.insert(0, match.name)

    self.reg_dob.delete(0, tk.END)
    self.reg_dob.insert(0, match.dob)

    self.reg_gender.set(match.gender)

    self.reg_contact.delete(0, tk.END)
    self.reg_contact.insert(0, match.contact_info)

    self.reg_address.delete(0, tk.END)
    self.reg_address.insert(0, match.address or "")

    messagebox.showinfo(
        "Loaded", f"Loaded details for {match.name} ({match.patient_id})"
    )

  def _handle_register_patient(self):
    if not self.auth.can_register_patient():
      messagebox.showerror(
          "Permission Denied", "Only Admin users can register new patients."
      )
      return

    name = self.reg_name.get().strip()
    dob = self.reg_dob.get().strip()
    gender = self.reg_gender.get()
    contact = self.reg_contact.get().strip()
    address = self.reg_address.get().strip()

    if not name or not dob or not gender or not contact:
      messagebox.showwarning(
          "Warning",
          "Please fill in all required fields (Name, DOB, Gender, Contact).",
      )
      return

    patient = self.patient_mgr.register_patient(
        name, dob, gender, contact, address
    )
    messagebox.showinfo(
        "Success",
        "Patient registered successfully!\nGenerated Patient ID:"
        f" {patient.patient_id}",
    )
    self._clear_reg_fields()

  def _handle_update_patient(self):
    if not self.auth.can_update_patient():
      messagebox.showerror(
          "Permission Denied", "Only Admin users can update patient details."
      )
      return

    pid = self.edit_pid_entry.get().strip()
    if not pid:
      messagebox.showwarning(
          "Warning", "Please load a Patient ID in the top field first."
      )
      return

    name = self.reg_name.get().strip()
    dob = self.reg_dob.get().strip()
    gender = self.reg_gender.get()
    contact = self.reg_contact.get().strip()
    address = self.reg_address.get().strip()

    if not name or not dob or not gender or not contact:
      messagebox.showwarning("Warning", "Fields cannot be left blank.")
      return

    self.patient_mgr.update_patient(pid, name, dob, gender, contact, address)
    messagebox.showinfo(
        "Success", f"Demographic details for Patient {pid} updated successfully!"
    )
    self._clear_reg_fields()

  def _clear_reg_fields(self):
    self.edit_pid_entry.delete(0, tk.END)
    self.reg_name.delete(0, tk.END)
    self.reg_dob.delete(0, tk.END)
    self.reg_contact.delete(0, tk.END)
    self.reg_address.delete(0, tk.END)

  # --- TAB 3: VISIT NOTES ---

  def _build_visits_tab(self):
    target_frame = ttk.LabelFrame(
        self.tab_visits, text="Patient Selection", padding="5"
    )
    target_frame.pack(fill=tk.X, pady=5)

    ttk.Label(target_frame, text="Patient ID:").pack(side=tk.LEFT, padx=5)
    self.visit_pid_entry = ttk.Entry(target_frame, width=20)
    self.visit_pid_entry.pack(side=tk.LEFT, padx=5)

    load_history_btn = ttk.Button(
        target_frame, text="Load History", command=self._handle_load_history
    )
    load_history_btn.pack(side=tk.LEFT, padx=5)

    note_frame = ttk.LabelFrame(
        self.tab_visits, text="New Clinical Note", padding="5"
    )
    note_frame.pack(fill=tk.BOTH, expand=True, pady=5)

    self.note_text = tk.Text(note_frame, height=5)
    self.note_text.pack(fill=tk.BOTH, expand=True, pady=5)

    cat_frame = ttk.Frame(note_frame)
    cat_frame.pack(fill=tk.X, pady=5)

    ttk.Label(cat_frame, text="Assigned Category:").pack(
        side=tk.LEFT, padx=(0, 5)
    )

    self.category_combo = ttk.Combobox(
        cat_frame,
        values=[
            "Uncategorized",
            "Cardiology",
            "General Practice",
            "Orthopedics",
            "Pediatrics",
            "Other",
        ],
        state="normal",
        width=25,
    )
    self.category_combo.set("Uncategorized")
    self.category_combo.pack(side=tk.LEFT, padx=5)

    get_ai_btn = ttk.Button(
        cat_frame, text="Get AI Suggestion", command=self._handle_get_ai_category
    )
    get_ai_btn.pack(side=tk.LEFT, padx=5)

    self.sim_timeout_var = tk.BooleanVar(value=False)
    self.timeout_chk = ttk.Checkbutton(
        cat_frame, text="Simulate Timeout", variable=self.sim_timeout_var
    )
    self.timeout_chk.pack(side=tk.LEFT, padx=10)

    save_note_btn = ttk.Button(
        note_frame, text="Save Visit Note", command=self._handle_save_visit_note
    )
    save_note_btn.pack(anchor=tk.E, pady=5)

    history_frame = ttk.LabelFrame(
        self.tab_visits, text="Past Visit Notes & Saved Categories", padding="5"
    )
    history_frame.pack(fill=tk.BOTH, expand=True, pady=5)

    self.history_box = tk.Text(history_frame, height=6, state=tk.DISABLED)
    self.history_box.pack(fill=tk.BOTH, expand=True)

  def _handle_get_ai_category(self):
    text = self.note_text.get("1.0", tk.END).strip()
    if not text:
      messagebox.showwarning(
          "Warning", "Please enter note text first to generate a suggestion."
      )
      return

    suggestion = self.ai_client.suggest_category(
        text, simulate_timeout=self.sim_timeout_var.get()
    )
    self.category_combo.set(suggestion)

  def _handle_load_history(self):
    pid = self.visit_pid_entry.get().strip()
    if not pid:
      messagebox.showwarning("Warning", "Please enter a Patient ID.")
      return

    notes = self.visit_mgr.get_patient_history(pid)
    self.history_box.config(state=tk.NORMAL)
    self.history_box.delete("1.0", tk.END)

    if not notes:
      self.history_box.insert(
          tk.END, f"No visit notes found for Patient ID: {pid}\n"
      )
    else:
      for n in notes:
        entry = (
            f"[{n.timestamp}] Clinician: {n.clinician_id}\n"
            f"CATEGORY STORED: {n.category or 'None'}\n"
            f"Note: {n.note_body}\n"
            f"{'-'*50}\n"
        )
        self.history_box.insert(tk.END, entry)
    self.history_box.config(state=tk.DISABLED)

  def _handle_save_visit_note(self):
    pid = self.visit_pid_entry.get().strip()
    text = self.note_text.get("1.0", tk.END).strip()
    final_category = self.category_combo.get().strip()

    if not pid:
      messagebox.showwarning("Warning", "Please provide a Patient ID.")
      return

    if not text:
      messagebox.showwarning("Warning", "Note body cannot be empty.")
      return

    self._save_visit_note(pid, text, final_category)

  def _save_visit_note(self, patient_id, note_text, category):
    if not self.auth.can_add_visit_note():
      messagebox.showerror(
          "Permission Denied", "Clinical role required to add notes."
      )
      return

    self.visit_mgr.add_visit_note(
        patient_id=patient_id,
        clinician_id=self.auth.current_user["username"],
        note_body=note_text,
        category=category,
    )
    messagebox.showinfo(
        "Success", f"Visit note saved with category: '{category}'"
    )

    self.note_text.delete("1.0", tk.END)
    self.category_combo.set("Uncategorized")
    self._handle_load_history()


if __name__ == "__main__":
  db_manager = DatabaseManager("prs.db")
  auth_service = AuthService()
  patient_manager = PatientManager(db_manager)
  visit_manager = VisitManager(db_manager)
  ai_client = AIServiceClient()

  auth_service.login(username="admin_user", role="admin")

  root = tk.Tk()
  app = PRSApp(
      root=root,
      auth_service=auth_service,
      patient_manager=patient_manager,
      visit_manager=visit_manager,
      ai_client=ai_client,
  )
  root.mainloop()