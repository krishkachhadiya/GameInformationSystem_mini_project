import csv
import os
import tkinter as tk
from tkinter import ttk, messagebox

# ---------------- CONFIG ----------------
FNAME = "games.csv"
COLUMNS = ['name', 'type', 'release_date', 'developer', 'platform',
           'downloads', 'version', 'rating', 'min_age']

# ---------------- STORAGE HELPERS ----------------
def ensure_file():
    if not os.path.exists(FNAME):
        with open(FNAME, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(COLUMNS)

def read_rows():
    ensure_file()
    with open(FNAME, "r", newline="") as f:
        rows = list(csv.reader(f))
    return [r for r in rows[1:] if len(r) == len(COLUMNS)]

def write_rows(rows):
    with open(FNAME, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(COLUMNS)
        writer.writerows(rows)

# ---------------- GUI APP ----------------
class GameGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🎮 Game Management System")
        self.geometry("1250x650")
        self.minsize(1100, 600)

        self.full_rows = []
        self.view_rows = []
        self.sort_states = {"rating": True, "platform": True}

        self._build_ui()
        self.load_all()

    def _build_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # ---------- Top Controls ----------
        btn_frame = ttk.Frame(self, padding=10)
        btn_frame.grid(row=0, column=0, columnspan=2, sticky="we")

        ttk.Button(btn_frame, text="Add Game", command=self.add_game).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Update Selected", command=self.update_selected).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Delete Selected", command=self.delete_selected).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Sort by Rating", command=self.sort_by_rating).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Sort by Platform", command=self.sort_by_platform).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Highest Rated", command=self.show_highest_rated).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Refresh", command=self.load_all).pack(side="left", padx=5)

        # ---- Search Box ----
        self.search_var = tk.StringVar()
        ttk.Entry(btn_frame, textvariable=self.search_var, width=25).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Search Game", command=self.search_game).pack(side="left", padx=5)

        ttk.Button(btn_frame, text="Exit", command=self.destroy).pack(side="right", padx=5)

        # ---------- Left: Form ----------
        form_frame = ttk.LabelFrame(self, text="Game Details", padding=10)
        form_frame.grid(row=1, column=0, sticky="nsw", padx=10, pady=10)

        self.form_vars = {c: tk.StringVar() for c in COLUMNS}
        r = 0
        for col in COLUMNS:
            ttk.Label(form_frame, text=col.replace("_", " ").title()).grid(row=r, column=0, sticky="w", pady=4)
            ttk.Entry(form_frame, textvariable=self.form_vars[col], width=30).grid(row=r, column=1, pady=4)
            r += 1

        ttk.Button(form_frame, text="Clear Form", command=self.clear_form).grid(row=r, column=0, columnspan=2, pady=10)

        # ---------- Right: Table ----------
        table_frame = ttk.Frame(self, padding=10)
        table_frame.grid(row=1, column=1, sticky="nsew")
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(table_frame, columns=COLUMNS, show="headings", selectmode="browse")
        for col in COLUMNS:
            self.tree.heading(col, text=col.title())
            self.tree.column(col, width=120, anchor="center")
        self.tree.column("name", width=180, anchor="w")
        self.tree.column("developer", width=160, anchor="w")
        self.tree.grid(row=0, column=0, sticky="nsew")

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscroll=vsb.set, xscroll=hsb.set)
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="we")

        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

    # ---------- Data / View ----------
    def load_all(self):
        self.full_rows = read_rows()
        self.view_rows = list(self.full_rows)
        self.refresh_table()

    def refresh_table(self):
        for iid in self.tree.get_children():
            self.tree.delete(iid)
        for row in self.view_rows:
            self.tree.insert("", "end", values=row)

    def clear_form(self):
        for v in self.form_vars.values():
            v.set("")

    def on_tree_select(self, _ev=None):
        sel = self.tree.selection()
        if not sel:
            return
        values = self.tree.item(sel[0], "values")
        for i, col in enumerate(COLUMNS):
            self.form_vars[col].set(values[i])

    def _selected_index_in_full(self):
        sel = self.tree.selection()
        if not sel:
            return None
        values = list(self.tree.item(sel[0], "values"))
        for i, r in enumerate(self.full_rows):
            if r == values:
                return i
        return None

    # ---------- Actions ----------
    def add_game(self):
        row = [self.form_vars[c].get().strip() for c in COLUMNS]
        ok, msg = self._validate_row(row)
        if not ok:
            messagebox.showerror("Invalid data", msg)
            return
        self.full_rows.append(row)
        write_rows(self.full_rows)
        self.load_all()
        self.clear_form()
        messagebox.showinfo("Added", "Game added successfully.")

    def update_selected(self):
        idx = self._selected_index_in_full()
        if idx is None:
            messagebox.showwarning("Select", "Select a row to update.")
            return
        row = [self.form_vars[c].get().strip() for c in COLUMNS]
        ok, msg = self._validate_row(row)
        if not ok:
            messagebox.showerror("Invalid data", msg)
            return
        self.full_rows[idx] = row
        write_rows(self.full_rows)
        self.load_all()
        messagebox.showinfo("Updated", "Game updated successfully.")

    def delete_selected(self):
        idx = self._selected_index_in_full()
        if idx is None:
            messagebox.showwarning("Select", "Select a row to delete.")
            return
        name = self.full_rows[idx][0]
        if not messagebox.askyesno("Confirm", f"Delete '{name}'?"):
            return
        del self.full_rows[idx]
        write_rows(self.full_rows)
        self.load_all()
        self.clear_form()
        messagebox.showinfo("Deleted", f"'{name}' deleted.")

    def sort_by_rating(self):
        col_index = COLUMNS.index("rating")
        self.view_rows = sorted(
            self.view_rows,
            key=lambda r: float(r[col_index]) if r[col_index].replace('.', '', 1).isdigit() else -1,
            reverse=True
        )
        self.sort_states["rating"] = not self.sort_states["rating"]
        self.refresh_table()

    def sort_by_platform(self):
        col_index = COLUMNS.index("platform")
        self.view_rows = sorted(
            self.view_rows,
            key=lambda r: r[col_index].lower(),
            reverse=not self.sort_states["platform"]
        )
        self.sort_states["platform"] = not self.sort_states["platform"]
        self.refresh_table()

    def show_highest_rated(self):
        best = None
        best_val = -1.0
        for r in self.full_rows:
            try:
                v = float(r[7])
            except:
                continue
            if v > best_val:
                best_val = v
                best = r
        if not best:
            messagebox.showinfo("No Ratings", "No valid rated games found.")
            return
        self.view_rows = [best]
        self.refresh_table()
        messagebox.showinfo("Highest Rated", f"{best[0]} — Rating: {best[7]}")

    def search_game(self):
        term = self.search_var.get().strip().lower()
        if not term:
            self.load_all()
            return
        self.view_rows = [r for r in self.full_rows if term in r[0].lower()]
        if not self.view_rows:
            messagebox.showinfo("Search", f"No game found matching '{term}'.")
        self.refresh_table()

    # ---------- Validation ----------
    def _validate_row(self, row):
        if any(not v for v in row):
            return False, "All fields are required."
        try:
            int(row[5])
        except:
            return False, "Downloads must be an integer."
        try:
            r = float(row[7])
            if r < 0 or r > 10:
                return False, "Rating must be 0-10."
        except:
            return False, "Rating must be a number (0-10)."
        try:
            int(row[8])
        except:
            return False, "Min Age must be integer."
        d = row[2]
        if not (len(d) == 10 and d[2] == "-" and d[5] == "-" and all(part.isdigit() for part in d.split("-"))):
            return False, "Release Date must be DD-MM-YYYY."
        return True, ""

# ---------------- RUN ----------------
if __name__ == "__main__":
    ensure_file()
    app = GameGUI()
    app.mainloop()
