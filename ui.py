""" STUDENT MANAGEMENT SYSTEM - TKINTER UI  """

import tkinter as tk
from tkinter import ttk, messagebox

import student_logic as logic

# color palette 
BG_DARK = "#1f2937"      
BG_APP = "#f3f4f6"        #background
ACCENT = "#4f46e5"      
ACCENT_HOVER = "#4338ca"
DANGER = "#dc2626"
DANGER_HOVER = "#b91c1c"
TEXT_LIGHT = "#f9fafb"
ROW_EVEN = "#ffffff"
ROW_ODD = "#eef2ff"

GRADE_COLORS = {
    "A+": "#16a34a", "A": "#22c55e", "B": "#0ea5e9",
    "C": "#f59e0b", "F": "#ef4444",
}

COLUMNS = ("roll", "name", "city", "maths", "science", "english",
           "total", "average", "percentage", "grade")

COLUMN_HEADINGS = {
    "roll": "Roll", "name": "Name", "city": "City/Course",
    "maths": "Maths", "science": "Science", "english": "English",
    "total": "Total", "average": "Avg", "percentage": "%", "grade": "Grade",
}


def center_window(win, parent):
    win.update_idletasks()
    width = win.winfo_width()
    height = win.winfo_height()
    x = parent.winfo_x() + (parent.winfo_width() // 2) - (width // 2)
    y = parent.winfo_y() + (parent.winfo_height() // 2) - (height // 2)
    win.geometry(f"{width}x{height}+{x}+{y}")


class ActionButton(tk.Button):
    """A flat, colored button with a hover effect (nicer than default ttk button)."""

    def __init__(self, parent, text, command, bg=ACCENT, hover=ACCENT_HOVER, **kwargs):
        super().__init__(
            parent, text=text, command=command,
            bg=bg, fg="white", activebackground=hover, activeforeground="white",
            font=("Segoe UI", 10, "bold"), relief="flat", bd=0,
            padx=14, pady=8, cursor="hand2", **kwargs,
        )
        self._bg = bg
        self._hover = hover
        self.bind("<Enter>", lambda e: self.config(bg=self._hover))
        self.bind("<Leave>", lambda e: self.config(bg=self._bg))


class StudentApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Student Management System")
        self.geometry("1000x560")
        self.minsize(880, 480)
        self.configure(bg=BG_APP)

        self._setup_style()
        self._build_header()
        self._build_toolbar()
        self._build_table()
        self._build_statusbar()
        self.refresh_table()

    # style

    def _setup_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure(
            "Treeview",
            background=ROW_EVEN,
            fieldbackground=ROW_EVEN,
            foreground="#111827",
            rowheight=30,
            font=("Segoe UI", 10),
            borderwidth=0,
        )
        style.configure(
            "Treeview.Heading",
            background=BG_DARK,
            foreground=TEXT_LIGHT,
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            padding=6,
        )
        style.map("Treeview.Heading", background=[("active", BG_DARK)])
        style.map("Treeview", background=[("selected", ACCENT)], foreground=[("selected", "white")])

 # construction

    def _build_header(self):
        header = tk.Frame(self, bg=BG_DARK, height=64)
        header.pack(side="top", fill="x")
        header.pack_propagate(False)

        tk.Label(
            header, text="\U0001F393  Student Management System",
            bg=BG_DARK, fg=TEXT_LIGHT, font=("Segoe UI", 16, "bold"),
            padx=18,
        ).pack(side="left")

    def _build_toolbar(self):
        bar = tk.Frame(self, bg=BG_APP, padx=12, pady=10)
        bar.pack(side="top", fill="x")

        left_buttons = [
            ("+ Add", self.open_add_dialog, ACCENT, ACCENT_HOVER),
            ("Edit Update", self.open_update_dialog, ACCENT, ACCENT_HOVER),
            ("Delete", self.delete_selected, DANGER, DANGER_HOVER),
            ("Search", self.open_search_dialog, ACCENT, ACCENT_HOVER),
        ]
        right_buttons = [
            ("Passed", self.show_passed, "#0f766e", "#115e59"),
            ("Sort by Marks", self.sort_by_marks, "#0f766e", "#115e59"),
            ("Class Average", self.show_class_average, "#0f766e", "#115e59"),
            ("Unique Cities", self.show_unique_cities, "#0f766e", "#115e59"),
            ("Show All", self.refresh_table, "#6b7280", "#4b5563"),
        ]

        for text, cmd, bg, hover in left_buttons:
            ActionButton(bar, text, cmd, bg=bg, hover=hover).pack(side="left", padx=(0, 6))

        for text, cmd, bg, hover in right_buttons:
            ActionButton(bar, text, cmd, bg=bg, hover=hover).pack(side="left", padx=(6, 0))

    def _build_table(self):
        frame = tk.Frame(self, bg=BG_APP, padx=12)
        frame.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(frame, columns=COLUMNS, show="headings", selectmode="browse")
        for col in COLUMNS:
            self.tree.heading(col, text=COLUMN_HEADINGS[col])
            width = 150 if col == "name" else 90
            self.tree.column(col, width=width, anchor="center")

        self.tree.tag_configure("evenrow", background=ROW_EVEN)
        self.tree.tag_configure("oddrow", background=ROW_ODD)
        for grade, color in GRADE_COLORS.items():
            self.tree.tag_configure(f"grade_{grade}", foreground=color, font=("Segoe UI", 10, "bold"))

        vsb = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True, pady=(0, 12))
        vsb.pack(side="right", fill="y", pady=(0, 12))

    def _build_statusbar(self):
        self.status_var = tk.StringVar(value="Ready.")
        bar = tk.Label(
            self, textvariable=self.status_var, bg=BG_DARK, fg=TEXT_LIGHT,
            anchor="w", padx=12, font=("Segoe UI", 9), height=1,
        )
        bar.pack(side="bottom", fill="x")

    def set_status(self, text):
        self.status_var.set(text)

    # table helpers 

    def refresh_table(self, students=None):
        self.tree.delete(*self.tree.get_children())
        data = students if students is not None else logic.get_all_students()
        for i, s in enumerate(data):
            stripe = "evenrow" if i % 2 == 0 else "oddrow"
            grade_tag = f"grade_{s['grade']}"
            self.tree.insert("", "end", values=(
                s["roll"], s["name"], s["city"],
                s["marks"]["Maths"], s["marks"]["Science"], s["marks"]["English"],
                s["total"], s["average"], s["percentage"], s["grade"],
            ), tags=(stripe, grade_tag))
        self.set_status(f"Showing {len(data)} student(s)   |   "
                         f"Total added this session: {logic.total_students_added}")

    def get_selected_roll(self):
        selection = self.tree.selection()
        if not selection:
            return None
        values = self.tree.item(selection[0], "values")
        return int(values[0])

    

    def delete_selected(self):
        roll = self.get_selected_roll()
        if roll is None:
            messagebox.showinfo("Delete Student", "Select a student in the table first.")
            return
        target = logic.find_student(roll)
        name = target["name"] if target else roll
        if not messagebox.askyesno("Confirm Delete", f"Delete '{name}' (Roll {roll})?"):
            return
        success, message = logic.delete_student(roll)
        (messagebox.showinfo if success else messagebox.showerror)("Delete Student", message)
        if success:
            self.refresh_table()

    def open_search_dialog(self):
        roll = SimpleInputDialog.ask_int(self, "Search Student", "Enter roll number:")
        if roll is None:
            return
        student = logic.find_student(roll)
        if student is None:
            messagebox.showinfo("Search Student", "No student found with that roll number.")
            return
        self.refresh_table([student])
        self.set_status(f"Search result for roll {roll}.")

    def show_passed(self):
        self.refresh_table(logic.get_passed_students())

    def sort_by_marks(self):
        self.refresh_table(logic.get_sorted_students())

    def show_class_average(self):
        result = logic.get_class_average()
        if result is None:
            messagebox.showinfo("Class Average", "No records found.")
            return
        grand_total, class_average, per_student = result
        lines = [f"Number of students   : {len(logic.students)}",
                 f"Grand total marks    : {grand_total}",
                 f"Class average (total): {class_average}", "", "Individual percentages:"]
        for s, pct in per_student:
            lines.append(f"  {s['name']:<20}: {pct}%")
        messagebox.showinfo("Class Average", "\n".join(lines))

    def show_unique_cities(self):
        cities = logic.get_unique_cities()
        if not cities:
            messagebox.showinfo("Unique Cities/Courses", "No records found.")
            return
        messagebox.showinfo("Unique Cities/Courses", "\n".join(f"- {c}" for c in sorted(cities)))

    def open_add_dialog(self):
        StudentFormDialog(self, mode="add")

    def open_update_dialog(self):
        roll = self.get_selected_roll()
        if roll is None:
            roll = SimpleInputDialog.ask_int(self, "Update Student", "Enter roll number to update:")
            if roll is None:
                return
        student = logic.find_student(roll)
        if student is None:
            messagebox.showerror("Update Student", "No student found with that roll number.")
            return
        StudentFormDialog(self, mode="update", student=student)


class SimpleInputDialog:

    @staticmethod
    def ask_int(parent, title, prompt):
        dialog = tk.Toplevel(parent)
        dialog.title(title)
        dialog.configure(bg=BG_APP)
        dialog.transient(parent)
        dialog.grab_set()
        dialog.resizable(False, False)

        tk.Label(dialog, text=prompt, bg=BG_APP, font=("Segoe UI", 10)).pack(padx=18, pady=(18, 6))
        var = tk.StringVar()
        entry = tk.Entry(dialog, textvariable=var, font=("Segoe UI", 10), relief="solid", bd=1)
        entry.pack(padx=18, pady=6, ipady=4)
        entry.focus()

        result = {"value": None}

        def submit():
            try:
                result["value"] = int(var.get())
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter a whole number.", parent=dialog)

        ActionButton(dialog, "OK", submit).pack(pady=(6, 18))
        dialog.bind("<Return>", lambda e: submit())
        center_window(dialog, parent)
        parent.wait_window(dialog)
        return result["value"]


class StudentFormDialog(tk.Toplevel):

    def __init__(self, parent, mode, student=None):
        super().__init__(parent)
        self.parent = parent
        self.mode = mode
        self.student = student
        self.configure(bg=BG_APP)

        self.title("Add Student" if mode == "add" else f"Update Student (Roll {student['roll']})")
        self.transient(parent)
        self.grab_set()
        self.resizable(False, False)

        self.vars = {
            "name": tk.StringVar(),
            "city": tk.StringVar(),
            "roll": tk.StringVar(),
        }
        self.mark_vars = {subject: tk.StringVar() for subject in logic.SUBJECTS}

        if mode == "update":
            self.vars["name"].set("")   # blank = unchanged, per original CLI behaviour
            self.vars["city"].set("")
            self.vars["roll"].set(str(student["roll"]))

        self._build_form()
        center_window(self, parent)

    def _field(self, row, label_text):
        tk.Label(self, text=label_text, bg=BG_APP, font=("Segoe UI", 10)).grid(
            row=row, column=0, sticky="e", padx=(16, 8), pady=6)

    def _build_form(self):
        tk.Frame(self, bg=ACCENT, height=6).grid(row=0, column=0, columnspan=2, sticky="ew")
        row = 1

        placeholder_name = self.student["name"] if self.mode == "update" else ""
        placeholder_city = self.student["city"] if self.mode == "update" else ""

        self._field(row, f"Name{f' [{placeholder_name}]' if placeholder_name else ''}:")
        tk.Entry(self, textvariable=self.vars["name"], font=("Segoe UI", 10),
                 relief="solid", bd=1).grid(row=row, column=1, padx=(0, 16), pady=6, ipady=3)
        row += 1

        self._field(row, f"City/Course{f' [{placeholder_city}]' if placeholder_city else ''}:")
        tk.Entry(self, textvariable=self.vars["city"], font=("Segoe UI", 10),
                 relief="solid", bd=1).grid(row=row, column=1, padx=(0, 16), pady=6, ipady=3)
        row += 1

        self._field(row, "Roll Number:")
        roll_state = "disabled" if self.mode == "update" else "normal"
        tk.Entry(self, textvariable=self.vars["roll"], font=("Segoe UI", 10),
                 relief="solid", bd=1, state=roll_state).grid(row=row, column=1, padx=(0, 16), pady=6, ipady=3)
        row += 1

        for subject in logic.SUBJECTS:
            existing = f" [{self.student['marks'][subject]}]" if self.mode == "update" else ""
            self._field(row, f"{subject}{existing}:")
            tk.Entry(self, textvariable=self.mark_vars[subject], font=("Segoe UI", 10),
                     relief="solid", bd=1).grid(row=row, column=1, padx=(0, 16), pady=6, ipady=3)
            row += 1

        btn_frame = tk.Frame(self, bg=BG_APP)
        btn_frame.grid(row=row, column=0, columnspan=2, pady=16)
        label = "Add Student" if self.mode == "add" else "Save Changes"
        ActionButton(btn_frame, label, self.submit).pack(side="left", padx=6)
        ActionButton(btn_frame, "Cancel", self.destroy, bg="#6b7280", hover="#4b5563").pack(side="left", padx=6)

        self.bind("<Return>", lambda e: self.submit())

    def _parse_marks(self, required):
        marks = {}
        for subject in logic.SUBJECTS:
            raw = self.mark_vars[subject].get().strip()
            if raw == "":
                if required:
                    messagebox.showerror("Invalid Input", f"Marks for {subject} are required.", parent=self)
                    return None
                continue
            try:
                marks[subject] = int(raw)
            except ValueError:
                messagebox.showerror("Invalid Input", f"Marks for {subject} must be a whole number.", parent=self)
                return None
        return marks

    def submit(self):
        if self.mode == "add":
            try:
                roll = int(self.vars["roll"].get())
            except ValueError:
                messagebox.showerror("Invalid Input", "Roll number must be a whole number.", parent=self)
                return
            marks = self._parse_marks(required=True)
            if marks is None:
                return
            success, message = logic.add_student(
                self.vars["name"].get(), self.vars["city"].get(), roll, marks)
        else:
            roll = self.student["roll"]
            marks = self._parse_marks(required=False)
            if marks is None:
                return
            success, message = logic.update_student(
                roll,
                new_name=self.vars["name"].get() or None,
                new_city=self.vars["city"].get() or None,
                new_marks=marks or None,
            )

        if success:
            messagebox.showinfo("Success", message, parent=self)
            self.destroy()
            self.parent.refresh_table()
        else:
            messagebox.showerror("Error", message, parent=self)


if __name__ == "__main__":
    app = StudentApp()
    app.mainloop()
