# ui_tk.py (full updated)
import tkinter as tk
from tkinter import ttk, messagebox
import pyperclip
import threading
import time
import os
import base64

from crypto_utils import derive_key, encrypt, decrypt
from storage import init_db, register_user, get_user, add_entry, view_entries, delete_entry
from password_generator import generate_password
from utils.auth import hash_password, verify_password
from utils.theme import apply_theme, toggle_theme, CURRENT_MODE
from utils.clipboard import copy_to_clipboard  # returns False if unsupported in container

# helper
def running_in_docker():
    return os.path.exists("/.dockerenv")


class AnimatedFrame(ttk.Frame):
    """A small helper that can slide in/out content frames for simple transitions."""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.place(in_=master, x=0, y=0, relwidth=1, relheight=1)
        self._visible = True

    def slide_in_from_right(self, duration_ms=200):
        # basic slide animation: move from x=width -> x=0
        w = self.winfo_width() or self.master.winfo_width() or 800
        steps = 12
        delay = max(1, int(duration_ms / steps))
        for i in range(steps + 1):
            x = int(w * (1 - i / steps))
            self.place_configure(x=x)
            self.update()
            self.after(delay)

    def slide_out_to_right(self, duration_ms=200):
        w = self.winfo_width() or self.master.winfo_width() or 800
        steps = 12
        delay = max(1, int(duration_ms / steps))
        for i in range(steps + 1):
            x = int(w * (i / steps))
            self.place_configure(x=x)
            self.update()
            self.after(delay)


class PasswordManagerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        apply_theme(self, mode="light")  # start in light mode
        self.title("Secure Password Manager")
        self.geometry("1100x700")
        self.minsize(900, 600)

        self.current_user_id = None
        self.key = None

        # layout frames
        self.sidebar_width = 220
        self.sidebar = ttk.Frame(self, width=self.sidebar_width)
        self.sidebar.pack(side="left", fill="y")
        self.container = ttk.Frame(self)
        self.container.pack(side="left", fill="both", expand=True)

        init_db()
        self._auth_screen()

    # ---------------------------
    # Authentication (Login / Register)
    # ---------------------------
    def _auth_screen(self):
        # clear sidebar initially (hide until login)
        for w in self.sidebar.winfo_children():
            w.destroy()
        for w in self.container.winfo_children():
            w.destroy()

        frame = ttk.Frame(self.container, padding=40)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        title = ttk.Label(frame, text="Secure Password Manager", font=("Segoe UI", 20, "bold"))
        title.pack(pady=(0, 20))

        ttk.Label(frame, text="Username:", font=("Segoe UI", 12)).pack(pady=(10, 4))
        self.username_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.username_var, width=35).pack()

        ttk.Label(frame, text="Master Password:", font=("Segoe UI", 12)).pack(pady=(15, 4))
        self.password_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.password_var, show="*", width=35).pack()

        ttk.Button(frame, text="Sign In", command=self._login_user).pack(pady=18)

        # small separator text and register button
        ttk.Label(frame, text="Are you a new user?", font=("Segoe UI", 11)).pack(pady=(8, 4))
        ttk.Button(frame, text="Register", command=self._register_screen).pack()

    def _register_screen(self):
        for w in self.container.winfo_children():
            w.destroy()

        frame = ttk.Frame(self.container, padding=32)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        title = ttk.Label(frame, text="Create New Account", font=("Segoe UI", 18, "bold"))
        title.pack(pady=(0, 20))

        ttk.Label(frame, text="Choose Username:", font=("Segoe UI", 12)).pack(pady=(8, 2))
        self.reg_user_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.reg_user_var, width=36).pack()

        ttk.Label(frame, text="Choose Password:", font=("Segoe UI", 12)).pack(pady=(12, 2))
        self.reg_pass_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.reg_pass_var, show="*", width=36).pack()

        ttk.Label(frame, text="Retype Password:", font=("Segoe UI", 12)).pack(pady=(12, 2))
        self.reg_pass2_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.reg_pass2_var, show="*", width=36).pack()

        ttk.Button(frame, text="Register", command=self._register_user_submit).pack(pady=18)
        ttk.Button(frame, text="Back to Sign In", command=self._auth_screen).pack()

    def _register_user_submit(self):
        username = self.reg_user_var.get().strip()
        password = self.reg_pass_var.get().strip()
        password2 = self.reg_pass2_var.get().strip()

        if not username or not password or not password2:
            messagebox.showwarning("Missing", "All fields are required.")
            return

        if password != password2:
            messagebox.showerror("Error", "Passwords do not match.")
            return

        if get_user(username):
            messagebox.showerror("Error", "Username already exists.")
            return

        pwd_hash_b64, salt_b64 = hash_password(password)
        register_user(username, pwd_hash_b64, salt_b64)

        messagebox.showinfo("Success", "Account created successfully! Please sign in.")
        self._auth_screen()

    def _login_user(self):
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()

        if not username or not password:
            messagebox.showwarning("Missing", "Please enter username and password.")
            return

        user = get_user(username)
        if not user:
            messagebox.showerror("Error", "User not found.")
            return

        user_id, _, stored_hash_b64, stored_salt_b64 = user
        if not verify_password(password, stored_hash_b64, stored_salt_b64):
            messagebox.showerror("Error", "Incorrect password.")
            return

        salt_bytes = base64.b64decode(stored_salt_b64)
        self.key = derive_key(password, salt_bytes)
        self.current_user_id = user_id

        # build sidebar now that user is authenticated
        self._build_sidebar()
        self._show_dashboard(animated=True)

    # ---------------------------
    # Sidebar & Navigation
    # ---------------------------
    def _build_sidebar(self):
        for w in self.sidebar.winfo_children():
            w.destroy()

        # Profile box with placeholder avatar
        prof_frame = ttk.Frame(self.sidebar, padding=12, style="Card.TFrame")
        prof_frame.pack(fill="x", padx=12, pady=(12, 6))

        # circle avatar using canvas
        canvas = tk.Canvas(prof_frame, width=48, height=48, bg=self.cget("bg"), highlightthickness=0)
        canvas.create_oval(4, 4, 44, 44, fill="#4E8BF5" if CURRENT_MODE == "light" else "#6EA0F8", outline="")
        canvas.grid(row=0, column=0, rowspan=2, padx=(0, 8))
        ttk.Label(prof_frame, text=f"User #{self.current_user_id}", font=("Segoe UI", 11, "bold")).grid(row=0, column=1, sticky="w")
        ttk.Button(prof_frame, text="Settings", command=self._open_settings).grid(row=1, column=1, sticky="w", pady=(6,0))

        # Nav buttons
        nav_frame = ttk.Frame(self.sidebar, padding=(12,8))
        nav_frame.pack(fill="both", expand=True)

        ttk.Button(nav_frame, text="Dashboard", command=lambda: self._show_dashboard(animated=True)).pack(fill="x", pady=6)
        ttk.Button(nav_frame, text="Passwords", command=lambda: self._show_passwords(animated=True)).pack(fill="x", pady=6)
        ttk.Button(nav_frame, text="Add Password", command=lambda: self._show_add_entry(animated=True)).pack(fill="x", pady=6)

        # Spacer then footer controls
        bottom = ttk.Frame(self.sidebar)
        bottom.pack(side="bottom", fill="x", pady=12, padx=12)

        ttk.Button(bottom, text="Toggle Theme", command=self._toggle_theme).pack(fill="x", pady=6)
        ttk.Button(bottom, text="Logout", command=self._logout).pack(fill="x", pady=6)

    # ---------------------------
    # Theme toggle
    # ---------------------------
    def _toggle_theme(self):
        new_mode = toggle_theme(self)  # returns mode
        # Rebuild minor UI elements to reflect theme (avatar color)
        self._build_sidebar()
        # also re-style current content by forcing a repopulate
        try:
            self._populate_tree()
        except Exception:
            pass

    # ---------------------------
    # Views and Animated Transitions
    # ---------------------------
    def _clear_container(self):
        for w in self.container.winfo_children():
            w.destroy()

    def _show_dashboard(self, animated=False):
        self._clear_container()
        frame = AnimatedFrame(self.container)
        frame.config(padding=20)
        # Dashboard cards
        cards = ttk.Frame(frame, padding=10)
        cards.pack(fill="both", expand=True, padx=20, pady=20)

        # stat card 1: total passwords
        rows = view_entries(self.current_user_id)
        total = len(rows) if rows else 0
        c1 = ttk.Frame(cards, style="Card.TFrame", padding=12)
        c1.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        ttk.Label(c1, text="Total Passwords", font=("Segoe UI", 11)).pack(anchor="w")
        ttk.Label(c1, text=str(total), font=("Segoe UI", 20, "bold")).pack(anchor="w", pady=(8,0))

        # stat card 2: sample
        c2 = ttk.Frame(cards, style="Card.TFrame", padding=12)
        c2.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        ttk.Label(c2, text="Generate", font=("Segoe UI", 11)).pack(anchor="w")
        ttk.Button(c2, text="Generate Password", command=self._generate_and_copy).pack(anchor="w", pady=8)

        cards.columnconfigure(0, weight=1)
        cards.columnconfigure(1, weight=1)

        if animated:
            frame.slide_in_from_right()
        self.current_view = frame

    def _show_passwords(self, animated=False):
        self._clear_container()
        frame = AnimatedFrame(self.container)
        frame.config(padding=8)

        top = ttk.Frame(frame, padding=(12,8))
        top.pack(fill="x")
        ttk.Button(top, text="Refresh", command=self._populate_tree).pack(side="left")
        ttk.Button(top, text="Add Entry", command=lambda: self._add_entry_dialog()).pack(side="left", padx=8)

        search_frame = ttk.Frame(frame, padding=(8,6))
        search_frame.pack(fill="x")
        ttk.Label(search_frame, text="Search:").pack(side="left")
        self.search_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.search_var).pack(side="left", padx=6)
        self.search_var.trace_add("write", lambda *a: self._populate_tree())

        cols = ("id", "site", "username", "password")
        self.tree = ttk.Treeview(frame, columns=cols, show="headings", height=18)
        for c, w in zip(cols, (60, 300, 220, 300)):
            self.tree.heading(c, text=c.upper())
            self.tree.column(c, width=w)
        self.tree.pack(fill="both", expand=True, padx=12, pady=12)
        self.tree.bind("<Double-1>", lambda e: self._on_double_click())

        self._populate_tree()
        if animated:
            frame.slide_in_from_right()
        self.current_view = frame

    def _show_add_entry(self, animated=False):
        # present the same add-entry dialog as before
        self._add_entry_dialog()
        # no main content change; keep previous view

    # ---------------------------
    # Populate table (passwords)
    # ---------------------------
    def _populate_tree(self):
        if not hasattr(self, "tree"):
            return
        for r in self.tree.get_children():
            self.tree.delete(r)
        rows = view_entries(self.current_user_id)
        q = (self.search_var.get().lower().strip() if hasattr(self, "search_var") else "")
        for r in rows:
            try:
                decrypted = decrypt(r[3], self.key).decode()
            except Exception:
                decrypted = "<decryption error>"
            if q and q not in (r[1].lower() + " " + r[2].lower()):
                continue
            self.tree.insert("", "end", values=(r[0], r[1], r[2], decrypted))

    # ---------------------------
    # Generate password (clipboard safe)
    # ---------------------------
    def _generate_and_copy(self):
        pwd = generate_password()
        # Try using copy_to_clipboard to respect Docker logic
        try:
            ok = copy_to_clipboard(pwd)
            if ok:
                messagebox.showinfo("Generated", "Password copied to clipboard.")
                return
        except Exception:
            ok = False

        # fallback: try pyperclip directly (may work if xclip installed)
        try:
            pyperclip.copy(pwd)
            messagebox.showinfo("Generated", "Password copied to clipboard.")
            return
        except Exception:
            pass

        # final fallback: show password
        messagebox.showinfo("Generated", f"Password:\n\n{pwd}\n\n(Clipboard not available)")

    # ---------------------------
    # Add Entry dialog & handlers
    # ---------------------------
    def _add_entry_dialog(self):
        dlg = AddEntryDialog(self, self.key, self.current_user_id)
        self.wait_window(dlg)
        if dlg.saved:
            try:
                self._populate_tree()
            except Exception:
                pass

    # ---------------------------
    # double click copy
    # ---------------------------
    def _on_double_click(self):
        sel = self.tree.selection()
        if not sel:
            return
        row = self.tree.item(sel[0])["values"]
        pwd = row[3]
        try:
            ok = copy_to_clipboard(pwd)
            if ok:
                messagebox.showinfo("Copied", "Password copied to clipboard.")
                return
        except Exception:
            ok = False
        try:
            pyperclip.copy(pwd)
            messagebox.showinfo("Copied", "Password copied to clipboard.")
            return
        except Exception:
            pass
        messagebox.showinfo("Copied", f"Password:\n\n{pwd}\n\n(Clipboard not available)")

    # ---------------------------
    # Settings / Profile
    # ---------------------------
    def _open_settings(self):
        # Simple settings window with profile + theme toggle + reset master password placeholder
        win = tk.Toplevel(self)
        win.title("Settings")
        win.geometry("420x320")
        apply_theme(win, mode=CURRENT_MODE)
        frm = ttk.Frame(win, padding=20)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text=f"Profile - User #{self.current_user_id}", font=("Segoe UI", 14, "bold")).pack(pady=(4,10))

        # Theme toggle
        ttk.Button(frm, text=f"Toggle Theme (current: {CURRENT_MODE})", command=lambda: [self._toggle_theme(), win.destroy(), self._open_settings()]).pack(pady=8)

        # Change master password (simple flow)
        def change_master():
            old = simpledialog.askstring("Old password", "Enter current master password:", show="*", parent=win)
            if old is None:
                return
            # verify current
            user = get_user_by_id(self.current_user_id)
            if not user:
                messagebox.showerror("Error", "User record not found.")
                return
            _, username, stored_hash, stored_salt = user
            if not verify_password(old, stored_hash, stored_salt):
                messagebox.showerror("Error", "Current password incorrect.")
                return
            new = simpledialog.askstring("New password", "Enter new master password:", show="*", parent=win)
            if new is None:
                return
            confirm = simpledialog.askstring("Confirm", "Retype new password:", show="*", parent=win)
            if new != confirm:
                messagebox.showerror("Error", "Passwords do not match.")
                return
            # perform update: here we will re-hash and update DB - storage currently has no update_user_password helper
            # For now just show success (you can ask me to add DB update)
            messagebox.showinfo("Not implemented", "Master password change is not implemented via UI yet.")
        ttk.Button(frm, text="Change Master Password", command=change_master).pack(pady=8)

        ttk.Button(frm, text="Close", command=win.destroy).pack(pady=14)

    # ---------------------------
    # Logout
    # ---------------------------
    def _logout(self):
        self.current_user_id = None
        self.key = None
        # remove sidebar items
        for w in self.sidebar.winfo_children():
            w.destroy()
        self._auth_screen()


# helper to get user by id - storage currently supports get_user(username) so add a simple implementation:
def get_user_by_id(user_id: int):
    # naive search (inefficient but fine for small dev DB)
    conn = None
    try:
        import sqlite3
        conn = sqlite3.connect("database/password_manager.db")
        c = conn.cursor()
        c.execute("SELECT id, username, password_hash, salt FROM users WHERE id = ?", (user_id,))
        row = c.fetchone()
        return row
    finally:
        if conn:
            conn.close()


# ---------------------------
# Add Entry dialog
# ---------------------------
class AddEntryDialog(tk.Toplevel):
    def __init__(self, parent, key, user_id):
        super().__init__(parent)
        self.title("Add Password Entry")
        self.geometry("620x320")
        apply_theme(self, mode=CURRENT_MODE)

        self.saved = False
        self.key = key
        self.user_id = user_id

        frm = ttk.Frame(self, padding=20)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text="Site:").grid(row=0, column=0, sticky="e", pady=8)
        self.site_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.site_var, width=48).grid(row=0, column=1, pady=8)

        ttk.Label(frm, text="Username:").grid(row=1, column=0, sticky="e", pady=8)
        self.user_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.user_var, width=48).grid(row=1, column=1, pady=8)

        ttk.Label(frm, text="Password:").grid(row=2, column=0, sticky="e", pady=8)
        self.pwd_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.pwd_var, show="*", width=48).grid(row=2, column=1, pady=8)

        ttk.Button(frm, text="Generate", command=self._generate_pwd).grid(row=2, column=2, padx=8)
        ttk.Button(frm, text="Save", command=self._save).grid(row=3, column=1, pady=18, sticky="e")

    def _generate_pwd(self):
        p = generate_password()
        self.pwd_var.set(p)
        # attempt clipboard
        try:
            ok = copy_to_clipboard(p)
            if ok:
                messagebox.showinfo("Generated", "Password copied to clipboard.")
                return
        except Exception:
            pass
        try:
            pyperclip.copy(p)
            messagebox.showinfo("Generated", "Password copied to clipboard.")
            return
        except Exception:
            pass
        messagebox.showinfo("Generated", f"Password:\n\n{p}\n\n(Clipboard not available)")

    def _save(self):
        site = self.site_var.get().strip()
        user = self.user_var.get().strip()
        pwd = self.pwd_var.get().strip()
        if not (site and user and pwd):
            messagebox.showwarning("Missing", "All fields are required.")
            return
        encrypted = encrypt(pwd, self.key)
        add_entry(self.user_id, site, user, encrypted, "")
        self.saved = True
        self.destroy()


if __name__ == "__main__":
    app = PasswordManagerApp()
    app.mainloop()
