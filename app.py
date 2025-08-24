import hashlib
import os
import sqlite3
import sys
import threading
import time
import csv
from datetime import datetime, timezone
from tkinter import Tk, StringVar, BooleanVar
from tkinter import filedialog, messagebox
from tkinter import ttk

APP_NAME = "Password Audit Tool"
APP_VERSION = "1.0.0"
APP_AUTHOR = "©Thorsten Bylicki | ©BYLICKILABS"
GITHUB_URL = "https://github.com/bylickilabs"
DB_FILENAME = "leaks.db"


LANG = {
    "DE": {
        "app_title": f"{APP_NAME} {APP_VERSION} {APP_AUTHOR}",
        "tab_single": "Einzel-Check",
        "tab_bulk": "Bulk-Audit",
        "tab_db": "Leak DB",
        "settings": "Einstellungen",
        "language": "Sprache",
        "theme": "Design",
        "light": "Hell",
        "dark": "Dunkel",
        "github": "GitHub",
        "info": "Info",
        "password": "Passwort",
        "show": "Anzeigen",
        "hide": "Verbergen",
        "check": "Prüfen",
        "result": "Ergebnis",
        "strength": "Stärke",
        "entropy": "Entropie (≈)",
        "found": "GELEAKT – in Datenbank gefunden",
        "not_found": "Nicht gefunden",
        "chars": "Zeichen",
        "classes": "Zeichenklassen",
        "len": "Länge",
        "class_lower": "Kleinbuchstaben",
        "class_upper": "Großbuchstaben",
        "class_digit": "Ziffern",
        "class_symbol": "Symbole",
        "import_leaks": "Leak-Datei importieren (.txt)",
        "db_stats": "Datenbank-Status",
        "entries": "Einträge",
        "last_import": "Letzter Import",
        "vacuum": "VACUUM/Optimieren",
        "import_running": "Import läuft…",
        "cancel": "Abbrechen",
        "bulk_source": "Passwortliste (eine Zeile = ein Passwort)",
        "choose_file": "Datei wählen",
        "run_audit": "Audit starten",
        "export_csv": "Ergebnis als CSV exportieren",
        "include_plain": "Klartext in Export aufnehmen (nicht empfohlen)",
        "status_ready": "Bereit.",
        "status_import_done": "Import abgeschlossen.",
        "status_audit_done": "Audit abgeschlossen.",
        "confirm_cancel": "Import abbrechen?",
        "db_init": "Datenbank initialisiert.",
        "ok": "OK",
        "error": "Fehler",
        "no_file": "Keine Datei gewählt.",
        "bulk_done": "Bulk-Audit abgeschlossen.",
        "about_title": "Über dieses Tool",
        "about_text": (
            f"{APP_NAME}\nVersion: {APP_VERSION}\n\n"
            "Offline-Überprüfung von Passwörtern gegen lokale Leak-Daten.\n"
            "Es werden NUR SHA-1-Hashes in der DB gespeichert.\n"
            "Keine Cloud, keine Telemetrie."
        ),
    },
    "EN": {
        "app_title": f"{APP_NAME} {APP_VERSION} {APP_AUTHOR}",
        "tab_single": "Single Check",
        "tab_bulk": "Bulk Audit",
        "tab_db": "Leak DB",
        "settings": "Settings",
        "language": "Language",
        "theme": "Theme",
        "light": "Light",
        "dark": "Dark",
        "github": "GitHub",
        "info": "Info",
        "password": "Password",
        "show": "Show",
        "hide": "Hide",
        "check": "Check",
        "result": "Result",
        "strength": "Strength",
        "entropy": "Entropy (≈)",
        "found": "LEAKED – found in database",
        "not_found": "Not found",
        "chars": "Characters",
        "classes": "Char Classes",
        "len": "Length",
        "class_lower": "Lowercase",
        "class_upper": "Uppercase",
        "class_digit": "Digits",
        "class_symbol": "Symbols",
        "import_leaks": "Import leak file (.txt)",
        "db_stats": "Database status",
        "entries": "Entries",
        "last_import": "Last Import",
        "vacuum": "VACUUM/Optimize",
        "import_running": "Import running…",
        "cancel": "Cancel",
        "bulk_source": "Password list (one per line)",
        "choose_file": "Choose file",
        "run_audit": "Run audit",
        "export_csv": "Export results as CSV",
        "include_plain": "Include plaintext in export (not recommended)",
        "status_ready": "Ready.",
        "status_import_done": "Import finished.",
        "status_audit_done": "Audit finished.",
        "confirm_cancel": "Cancel import?",
        "db_init": "Database initialized.",
        "ok": "OK",
        "error": "Error",
        "no_file": "No file selected.",
        "bulk_done": "Bulk audit finished.",
        "about_title": "About this tool",
        "about_text": (
            f"{APP_NAME}\nVersion: {APP_VERSION}\n\n"
            "Offline verification of passwords against local leak data.\n"
            "Only SHA-1 hashes are stored in the DB.\n"
            "No cloud, no telemetry."
        ),
    },
}


def sha1_hex(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest().upper()


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class LeakDB:
    def __init__(self, path: str):
        self.path = path
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(self.path, check_same_thread=False)
        self._conn.execute("PRAGMA journal_mode=WAL;")
        self._conn.execute("PRAGMA synchronous=NORMAL;")
        self._conn.execute("PRAGMA temp_store=MEMORY;")
        self._init_schema()

    def _init_schema(self):
        with self._conn:
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS leaks (
                    sha1 TEXT PRIMARY KEY,
                    count INTEGER NOT NULL
                )
                """
            )
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS meta (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
                """
            )

            self._conn.execute(
                "INSERT OR IGNORE INTO leaks(sha1,count) VALUES(?,?)",
                (sha1_hex("123456"), 1),
            )
            self._conn.execute(
                "INSERT OR IGNORE INTO leaks(sha1,count) VALUES(?,?)",
                (sha1_hex("password"), 1),
            )
            self._conn.execute(
                "INSERT OR IGNORE INTO leaks(sha1,count) VALUES(?,?)",
                (sha1_hex("qwerty"), 1),
            )
            self._set_meta("db_initialized", now_iso())

    def _set_meta(self, key: str, value: str):
        with self._conn:
            self._conn.execute(
                "INSERT INTO meta(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (key, value),
            )

    def get_meta(self, key: str):
        cur = self._conn.cursor()
        cur.execute("SELECT value FROM meta WHERE key=?", (key,))
        row = cur.fetchone()
        return row[0] if row else None

    def stats(self):
        cur = self._conn.cursor()
        cur.execute("SELECT COUNT(*) FROM leaks")
        total = cur.fetchone()[0]
        last = self.get_meta("last_import")
        return total, last

    def vacuum(self):
        with self._conn:
            self._conn.execute("VACUUM")

    def contains_sha1(self, sha1: str) -> int:
        cur = self._conn.cursor()
        cur.execute("SELECT count FROM leaks WHERE sha1=?", (sha1,))
        row = cur.fetchone()
        return int(row[0]) if row else 0

    def import_plaintext_file(self, filepath: str, cancel_flag: threading.Event, progress_cb=None):

        with self._conn:
            self._conn.execute("PRAGMA synchronous=OFF;")
            self._conn.execute("PRAGMA journal_mode=MEMORY;")
            self._conn.execute("PRAGMA locking_mode=EXCLUSIVE;")

        batch = []
        total = 0
        last_update = time.time()
        BATCH_SIZE = 5000


        def line_iter(path):
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        yield line
            except UnicodeDecodeError:
                with open(path, "r", encoding="latin-1", errors="ignore") as f:
                    for line in f:
                        yield line

        cur = self._conn.cursor()
        cur.execute("BEGIN TRANSACTION")
        try:
            for line in line_iter(filepath):
                if cancel_flag.is_set():
                    break
                pw = line.rstrip("\n\r")
                if not pw:
                    continue
                digest = sha1_hex(pw)
                batch.append((digest,))
                total += 1
                if len(batch) >= BATCH_SIZE:
                    cur.executemany(
                        "INSERT INTO leaks(sha1,count) VALUES(?,1) ON CONFLICT(sha1) DO UPDATE SET count=count+1",
                        batch,
                    )
                    batch.clear()
                    if progress_cb and time.time() - last_update > 0.3:
                        last_update = time.time()
                        progress_cb(total)
            if batch:
                cur.executemany(
                    "INSERT INTO leaks(sha1,count) VALUES(?,1) ON CONFLICT(sha1) DO UPDATE SET count=count+1",
                    batch,
                )
            self._conn.commit()
        except Exception:
            self._conn.rollback()
            raise
        finally:
            with self._conn:
                self._conn.execute("PRAGMA synchronous=NORMAL;")
                self._conn.execute("PRAGMA journal_mode=WAL;")
                self._conn.execute("PRAGMA locking_mode=NORMAL;")
            if not cancel_flag.is_set():
                self._set_meta("last_import", now_iso())
        return total



import math
import re

LOWER = re.compile(r"[a-z]")
UPPER = re.compile(r"[A-Z]")
DIGIT = re.compile(r"[0-9]")
SYMBOL = re.compile(r"[^A-Za-z0-9]")


def estimate_entropy_bits(pw: str) -> float:
    pool = 0
    if LOWER.search(pw):
        pool += 26
    if UPPER.search(pw):
        pool += 26
    if DIGIT.search(pw):
        pool += 10
    if SYMBOL.search(pw):
        pool += 33
    pool = max(pool, 1)
    return round(len(pw) * math.log2(pool), 2)


def classify_strength(pw: str) -> str:
    L = len(pw)
    classes = sum([
        1 if LOWER.search(pw) else 0,
        1 if UPPER.search(pw) else 0,
        1 if DIGIT.search(pw) else 0,
        1 if SYMBOL.search(pw) else 0,
    ])
    ent = estimate_entropy_bits(pw)

    if L >= 16 and classes >= 3 and ent >= 80:
        return "Strong"
    if L >= 12 and classes >= 3 and ent >= 60:
        return "Good"
    if L >= 8 and classes >= 2 and ent >= 40:
        return "Fair"
    return "Weak"



class App(Tk):
    def __init__(self):
        super().__init__()
        self.lang = StringVar(value="DE")
        self.status_text = StringVar(value=LANG[self.lang.get()]["status_ready"]) 
        self.show_pw = BooleanVar(value=False)
        self.include_plain = BooleanVar(value=False)
        self.bulk_path = StringVar(value="")

        self.db = LeakDB(os.path.join(self._app_dir(), DB_FILENAME))

        self.title(LANG[self.lang.get()]["app_title"])
        self.geometry("900x560")
        self.minsize(820, 520)

        self._build_style()
        self._build_ui()
        self._apply_lang()

    def _app_dir(self) -> str:
        return os.path.dirname(os.path.abspath(sys.argv[0]))


    def _build_style(self):
        self.style = ttk.Style(self)

        try:
            self.style.theme_use("clam")
        except Exception:
            pass
        self._apply_theme()

    def _apply_theme(self):
        bg = "#F8FAFC"
        fg = "#0F172A"
        entry_bg = "#FFFFFF"
        self.configure(bg=bg)
        self.style.configure("TFrame", background=bg)
        self.style.configure("TLabel", background=bg, foreground=fg)
        self.style.configure("TButton", foreground=fg)
        self.style.configure("TCheckbutton", background=bg, foreground=fg)
        self.style.configure("TLabelframe", background=bg, foreground=fg)
        self.style.configure("TLabelframe.Label", background=bg, foreground=fg)
        self.style.configure("Treeview", background=entry_bg, fieldbackground=entry_bg, foreground=fg)
        self.style.configure("TEntry", fieldbackground=entry_bg)

        self.style.configure("TNotebook", background=bg, tabposition="n")
        self.style.configure("TNotebook.Tab", padding=(12, 6))


    def _build_ui(self):
        top = ttk.Frame(self)
        top.pack(fill="x", padx=12, pady=8)


        self.lbl_brand = ttk.Label(top, text=APP_NAME, font=("Segoe UI", 13, "bold"))
        self.lbl_brand.pack(side="left")


        btn_github = ttk.Button(top, text=LANG[self.lang.get()]["github"], command=self._open_github)
        btn_info = ttk.Button(top, text=LANG[self.lang.get()]["info"], command=self._show_info)
        self.cmb_lang = ttk.Combobox(top, values=["DE", "EN"], width=4, state="readonly", textvariable=self.lang)
        self.cmb_lang.bind("<<ComboboxSelected>>", lambda e: self._apply_lang())
        for w in (btn_github, btn_info, self.cmb_lang):
            w.pack(side="right", padx=6)


        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True, padx=12, pady=(0, 12))


        self.tab_single = ttk.Frame(self.nb)
        self.tab_bulk = ttk.Frame(self.nb)
        self.tab_db = ttk.Frame(self.nb)
        self.nb.add(self.tab_single, text=LANG[self.lang.get()]["tab_single"]) 
        self.nb.add(self.tab_bulk, text=LANG[self.lang.get()]["tab_bulk"]) 
        self.nb.add(self.tab_db, text=LANG[self.lang.get()]["tab_db"]) 

        self._build_tab_single()
        self._build_tab_bulk()
        self._build_tab_db()


        status = ttk.Frame(self)
        status.pack(fill="x", padx=12, pady=(0, 10))
        self.lbl_status = ttk.Label(status, textvariable=self.status_text)
        self.lbl_status.pack(side="left")


    def _build_tab_single(self):
        frm = ttk.Frame(self.tab_single)
        frm.pack(fill="both", expand=True, padx=14, pady=14)

        row1 = ttk.Frame(frm)
        row1.pack(fill="x", pady=8)
        self.lbl_pw = ttk.Label(row1, text=LANG[self.lang.get()]["password"]) 
        self.ent_pw_var = StringVar()
        self.ent_pw = ttk.Entry(row1, textvariable=self.ent_pw_var, show="•", width=48)
        self.btn_show = ttk.Button(row1, text=LANG[self.lang.get()]["show"], command=self._toggle_show)
        self.btn_check = ttk.Button(row1, text=LANG[self.lang.get()]["check"], command=self._do_single_check)
        self.lbl_pw.pack(side="left", padx=(0, 8))
        self.ent_pw.pack(side="left", padx=(0, 8))
        self.btn_show.pack(side="left", padx=(0, 8))
        self.btn_check.pack(side="left")

        row2 = ttk.Frame(frm)
        row2.pack(fill="x", pady=8)
        self.lbl_result_title = ttk.Label(row2, text=LANG[self.lang.get()]["result"]) 
        self.lbl_result_val = ttk.Label(row2, text="—", font=("Segoe UI", 11, "bold"))
        self.lbl_result_title.pack(side="left")
        self.lbl_result_val.pack(side="left", padx=(8, 0))

        row3 = ttk.Labelframe(frm, text=LANG[self.lang.get()]["strength"]) 
        row3.pack(fill="x", pady=8)
        loc = LANG[self.lang.get()]
        self.lbl_len = ttk.Label(row3, text=f"{loc['len']}: —") 
        self.lbl_classes = ttk.Label(row3, text=f"{loc['classes']}: —") 
        self.lbl_entropy = ttk.Label(row3, text=f"{loc['entropy']}: —") 
        for w in (self.lbl_len, self.lbl_classes, self.lbl_entropy):
            w.pack(anchor="w", padx=10, pady=3)


    def _build_tab_bulk(self):
        frm = ttk.Frame(self.tab_bulk)
        frm.pack(fill="both", expand=True, padx=14, pady=14)

        row1 = ttk.Frame(frm)
        row1.pack(fill="x", pady=8)
        self.lbl_bulk = ttk.Label(row1, text=LANG[self.lang.get()]["bulk_source"]) 
        self.ent_bulk = ttk.Entry(row1, textvariable=self.bulk_path, width=56)
        self.btn_choose = ttk.Button(row1, text=LANG[self.lang.get()]["choose_file"], command=self._choose_bulk)
        self.btn_run = ttk.Button(row1, text=LANG[self.lang.get()]["run_audit"], command=self._run_bulk)
        self.lbl_bulk.pack(side="left")
        self.ent_bulk.pack(side="left", padx=(8, 8))
        self.btn_choose.pack(side="left", padx=(0, 8))
        self.btn_run.pack(side="left")

        self.tree = ttk.Treeview(frm, columns=("plain", "sha1", "leaked", "count"), show="headings", height=16)
        self.tree.heading("plain", text="Plaintext")
        self.tree.heading("sha1", text="SHA-1")
        self.tree.heading("leaked", text="Leaked")
        self.tree.heading("count", text="Count")
        self.tree.column("plain", width=220)
        self.tree.column("sha1", width=270)
        self.tree.column("leaked", width=80, anchor="center")
        self.tree.column("count", width=80, anchor="e")
        self.tree.pack(fill="both", expand=True, pady=10)


        row2 = ttk.Frame(frm)
        row2.pack(fill="x", pady=6)
        self.chk_include_plain = ttk.Checkbutton(row2, text=LANG[self.lang.get()]["include_plain"], variable=self.include_plain)
        self.btn_export = ttk.Button(row2, text=LANG[self.lang.get()]["export_csv"], command=self._export_csv)
        self.chk_include_plain.pack(side="left")
        self.btn_export.pack(side="right")


    def _build_tab_db(self):
        frm = ttk.Frame(self.tab_db)
        frm.pack(fill="both", expand=True, padx=14, pady=14)


        row1 = ttk.Frame(frm)
        row1.pack(fill="x", pady=6)
        self.btn_import = ttk.Button(row1, text=LANG[self.lang.get()]["import_leaks"], command=self._import_leaks_dialog)
        self.btn_import.pack(side="left")


        row2 = ttk.Frame(frm)
        row2.pack(fill="x", pady=6)
        self.prg = ttk.Progressbar(row2, mode="indeterminate")
        self.btn_cancel = ttk.Button(row2, text=LANG[self.lang.get()]["cancel"], command=self._cancel_import, state="disabled")
        self.prg.pack(side="left", fill="x", expand=True)
        self.btn_cancel.pack(side="left", padx=8)


        grp = ttk.Labelframe(frm, text=LANG[self.lang.get()]["db_stats"]) 
        grp.pack(fill="x", pady=10)
        loc = LANG[self.lang.get()]
        self.lbl_entries = ttk.Label(grp, text=f"{loc['entries']}: —") 
        self.lbl_last = ttk.Label(grp, text=f"{loc['last_import']}: —") 
        self.btn_refresh = ttk.Button(grp, text=LANG[self.lang.get()]["ok"], command=self._refresh_stats)
        self.btn_vacuum = ttk.Button(grp, text=LANG[self.lang.get()]["vacuum"], command=self._do_vacuum)
        for w in (self.lbl_entries, self.lbl_last):
            w.pack(anchor="w", padx=10, pady=3)
        row3 = ttk.Frame(grp)
        row3.pack(fill="x", pady=6)
        self.btn_vacuum.pack(in_=row3, side="left")
        self.btn_refresh.pack(in_=row3, side="right")

        self._refresh_stats()


    def _apply_lang(self):
        loc = LANG[self.lang.get()]
        self.title(loc["app_title"])

        self.nb.tab(0, text=loc["tab_single"]) 
        self.nb.tab(1, text=loc["tab_bulk"]) 
        self.nb.tab(2, text=loc["tab_db"]) 

        self.lbl_pw.config(text=loc["password"]) 
        self.btn_show.config(text=loc["show"] if not self.show_pw.get() else loc["hide"]) 
        self.btn_check.config(text=loc["check"]) 
        self.lbl_result_title.config(text=loc["result"]) 
        self._refresh_strength_labels()

        self.lbl_bulk.config(text=loc["bulk_source"]) 
        self.btn_choose.config(text=loc["choose_file"]) 
        self.btn_run.config(text=loc["run_audit"]) 
        self.chk_include_plain.config(text=loc["include_plain"]) 
        self.btn_export.config(text=loc["export_csv"]) 

        self.btn_import.config(text=loc["import_leaks"]) 
        self.btn_cancel.config(text=loc["cancel"]) 
        self.lbl_entries.config(text=f"{loc['entries']}: —") 
        self.lbl_last.config(text=f"{loc['last_import']}: —") 
        self.btn_refresh.config(text=loc["ok"]) 
        self.btn_vacuum.config(text=loc["vacuum"]) 

        self.status_text.set(loc["status_ready"]) 

    def _refresh_strength_labels(self):
        loc = LANG[self.lang.get()]
        self.lbl_len.config(text=f"{loc['len']}: —") 
        self.lbl_classes.config(text=f"{loc['classes']}: —") 
        self.lbl_entropy.config(text=f"{loc['entropy']}: —") 

    def _toggle_show(self):
        self.show_pw.set(not self.show_pw.get())
        self.ent_pw.config(show="" if self.show_pw.get() else "•")
        loc = LANG[self.lang.get()]
        self.btn_show.config(text=loc["hide"] if self.show_pw.get() else loc["show"]) 

    def _open_github(self):
        import webbrowser
        webbrowser.open(GITHUB_URL)

    def _show_info(self):
        loc = LANG[self.lang.get()]
        messagebox.showinfo(loc["about_title"], loc["about_text"]) 

    def _do_single_check(self):
        loc = LANG[self.lang.get()]
        pw = self.ent_pw_var.get()
        if pw == "":
            self.lbl_result_val.config(text="—")
            self._refresh_strength_labels()
            return
        digest = sha1_hex(pw)
        count = self.db.contains_sha1(digest)
        leaked = count > 0
        self.lbl_result_val.config(text=(loc["found"] if leaked else loc["not_found"])) 

        L = len(pw)
        classes = sum([
            1 if LOWER.search(pw) else 0,
            1 if UPPER.search(pw) else 0,
            1 if DIGIT.search(pw) else 0,
            1 if SYMBOL.search(pw) else 0,
        ])
        ent = estimate_entropy_bits(pw)
        self.lbl_len.config(text=f"{loc['len']}: {L}") 
        flags = []
        if LOWER.search(pw):
            flags.append(loc['class_lower'])
        if UPPER.search(pw):
            flags.append(loc['class_upper'])
        if DIGIT.search(pw):
            flags.append(loc['class_digit'])
        if SYMBOL.search(pw):
            flags.append(loc['class_symbol'])
        self.lbl_classes.config(text=f"{loc['classes']}: {classes} ({', '.join(flags)})") 
        self.lbl_entropy.config(text=f"{loc['entropy']}: {ent} bits | {classify_strength(pw)}") 

    def _choose_bulk(self):
        path = filedialog.askopenfilename(title="Select file", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if path:
            self.bulk_path.set(path)

    def _run_bulk(self):
        loc = LANG[self.lang.get()]
        path = self.bulk_path.get()
        if not path or not os.path.exists(path):
            messagebox.showerror(loc["error"], loc["no_file"]) 
            return
        self.tree.delete(*self.tree.get_children())
        self.status_text.set("…")
        threading.Thread(target=self._bulk_worker, args=(path,), daemon=True).start()

    def _bulk_worker(self, path):
        loc = LANG[self.lang.get()]
        rows = []
        try:
            f = open(path, "r", encoding="utf-8", errors="ignore")
        except Exception:
            f = open(path, "r", encoding="latin-1", errors="ignore")
        with f:
            for line in f:
                pw = line.rstrip("\n\r")
                if pw == "":
                    continue
                digest = sha1_hex(pw)
                count = self.db.contains_sha1(digest)
                leaked = "YES" if count > 0 else "NO"
                rows.append((pw, digest, leaked, str(count)))
        def apply_rows():
            for r in rows[:5000]:
                self.tree.insert("", "end", values=r)
            idx = 5000
            def add_more():
                nonlocal idx
                chunk = 1000
                for r in rows[idx:idx+chunk]:
                    self.tree.insert("", "end", values=r)
                idx += chunk
                if idx < len(rows):
                    self.after(10, add_more)
                else:
                    self.status_text.set(loc["status_audit_done"]) 
            if idx < len(rows):
                self.after(10, add_more)
            else:
                self.status_text.set(loc["status_audit_done"]) 
        self.after(0, apply_rows)

    def _export_csv(self):
        loc = LANG[self.lang.get()]
        items = self.tree.get_children()
        if not items:
            return
        path = filedialog.asksaveasfilename(title="Export CSV", defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if not path:
            return
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)

            if self.include_plain.get():
                w.writerow(["plaintext", "sha1", "leaked", "count"]) 
            else:
                w.writerow(["sha1", "leaked", "count"]) 
            for it in items:
                vals = self.tree.item(it, "values")
                if self.include_plain.get():
                    w.writerow(vals)
                else:
                    w.writerow(vals[1:])
        messagebox.showinfo(APP_NAME, loc["bulk_done"]) 

    def _import_leaks_dialog(self):
        loc = LANG[self.lang.get()]
        path = filedialog.askopenfilename(title="Import leak file", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if not path:
            return
        self.status_text.set(loc["import_running"]) 
        self.prg.start(12)
        self.btn_cancel.config(state="normal")
        self._cancel_flag = threading.Event()
        threading.Thread(target=self._import_worker, args=(path,), daemon=True).start()

    def _cancel_import(self):
        loc = LANG[self.lang.get()]
        if hasattr(self, "_cancel_flag") and not self._cancel_flag.is_set():
            if messagebox.askyesno(APP_NAME, loc["confirm_cancel"]): 
                self._cancel_flag.set()

    def _import_worker(self, path):
        loc = LANG[self.lang.get()]
        try:
            total = self.db.import_plaintext_file(path, cancel_flag=self._cancel_flag, progress_cb=self._on_progress)
        except Exception as e:
            def on_err():
                self.prg.stop()
                self.btn_cancel.config(state="disabled")
                self.status_text.set(loc["error"]) 
                messagebox.showerror(APP_NAME, str(e)) 
            self.after(0, on_err)
            return

        def on_done():
            self.prg.stop()
            self.btn_cancel.config(state="disabled")
            self.status_text.set(loc["status_import_done"]) 
            self._refresh_stats()
        self.after(0, on_done)

    def _on_progress(self, total):
        pass

    def _refresh_stats(self):
        loc = LANG[self.lang.get()]
        entries, last = self.db.stats()
        self.lbl_entries.config(text=f"{loc['entries']}: {entries}") 
        self.lbl_last.config(text=f"{loc['last_import']}: {last or '—'}") 

    def _do_vacuum(self):
        self.db.vacuum()
        self._refresh_stats()


if __name__ == "__main__":
    app = App()
    app.mainloop()
