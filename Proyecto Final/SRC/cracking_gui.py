# cracking_gui.py
# DEMO EDUCATIVO CON GUI: solo probar contra CONTRASEÑAS/HASHES QUE POSEAS.
# No usar contra sistemas o cuentas sin permiso.

import hashlib, itertools, time, threading
from pathlib import Path
import string
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

# ---------------- CONFIG ----------------
plaintext_demo = "s3c"  # contraseña de ejemplo para generar el hash
HASH_ALGO = "sha256"
DEFAULT_ALPHABET = string.ascii_lowercase + string.digits
DEFAULT_MAX_LEN = 4
DEFAULT_WORDLIST_NAME = "wordlist.txt"
# ---------------------------------------

def hash_text(text, algo="sha256"):
    h = hashlib.new(algo)
    h.update(text.encode("utf-8"))
    return h.hexdigest()

def ensure_wordlist(path: Path, create_sample=False):
    if path.exists():
        return True
    if create_sample:
        sample = ["password", "123456", "admin", "letmein", "qwerty", "s3c", "welcome", "usuario", "contraseña"]
        path.write_text("\\n".join(sample), encoding="utf-8")
        return True
    return False

def dict_attack(target_hash, wordlist_path, algo="sha256", progress_callback=None, stop_event=None):
    path = Path(wordlist_path)
    start = time.time()
    if not path.exists():
        return None, 0.0, "NO_WORDLIST"
    with path.open("r", encoding="utf-8", errors="ignore") as f:
        for i, line in enumerate(f, 1):
            if stop_event and stop_event.is_set():
                return None, time.time() - start, "STOPPED"
            word = line.strip()
            if not word:
                continue
            if progress_callback and i % 1000 == 0:
                progress_callback(f"Dict checked: {i} words...")
            if hash_text(word, algo) == target_hash:
                elapsed = time.time() - start
                return word, elapsed, None
    elapsed = time.time() - start
    return None, elapsed, None

def brute_force_attack(target_hash, alphabet, max_len, algo="sha256", progress_callback=None, stop_event=None):
    start = time.time()
    total = 0
    for length in range(1, max_len+1):
        for tup in itertools.product(alphabet, repeat=length):
            if stop_event and stop_event.is_set():
                return None, time.time() - start, "STOPPED"
            candidate = "".join(tup)
            total += 1
            if progress_callback and total % 10000 == 0:
                progress_callback(f"Brute tried: {total} candidates (last: {candidate})")
            if hash_text(candidate, algo) == target_hash:
                elapsed = time.time() - start
                return candidate, elapsed, None
    elapsed = time.time() - start
    return None, elapsed, None

# -------- GUI App --------
class CrackingApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Cracking Demo (GUI) - Educativo")
        self.geometry("760x520")
        self.resizable(False, False)

        # Variables
        self.wordlist_path = tk.StringVar(value=str(Path(__file__).resolve().parent / DEFAULT_WORDLIST_NAME))
        self.alphabet = tk.StringVar(value=DEFAULT_ALPHABET)
        self.max_len = tk.IntVar(value=DEFAULT_MAX_LEN)
        self.status_var = tk.StringVar(value="Idle")
        self.stop_event = None
        self.thread = None

        # Top frame: configuration
        cfg = tk.LabelFrame(self, text="Configuración", padx=8, pady=8)
        cfg.place(x=10, y=10, width=740, height=140)

        tk.Label(cfg, text="Wordlist:").grid(row=0, column=0, sticky="w")
        tk.Entry(cfg, textvariable=self.wordlist_path, width=70).grid(row=0, column=1, padx=4)
        tk.Button(cfg, text="Examinar...", command=self.browse_wordlist).grid(row=0, column=2, padx=4)

        tk.Button(cfg, text="Crear wordlist de ejemplo", command=self.create_sample_wordlist).grid(row=1, column=1, sticky="w", pady=6)

        tk.Label(cfg, text="Alfabeto (para fuerza bruta):").grid(row=2, column=0, sticky="w")
        tk.Entry(cfg, textvariable=self.alphabet, width=40).grid(row=2, column=1, sticky="w", padx=4)
        tk.Label(cfg, text="Max Len:").grid(row=2, column=2, sticky="w")
        tk.Entry(cfg, textvariable=self.max_len, width=6).grid(row=2, column=2, sticky="e", padx=4)

        # Middle frame: controls and status
        ctrl = tk.LabelFrame(self, text="Controles", padx=8, pady=8)
        ctrl.place(x=10, y=160, width=740, height=80)

        tk.Button(ctrl, text="Ejecutar ataque por diccionario", command=self.run_dict).grid(row=0, column=0, padx=6)
        tk.Button(ctrl, text="Ejecutar fuerza bruta limitada", command=self.run_bruteforce).grid(row=0, column=1, padx=6)
        tk.Button(ctrl, text="Detener", command=self.stop_running, fg="red").grid(row=0, column=2, padx=6)
        tk.Label(ctrl, text="Estado:").grid(row=0, column=3, sticky="e")
        tk.Label(ctrl, textvariable=self.status_var, fg="blue").grid(row=0, column=4, sticky="w", padx=4)

        # Bottom frame: log/output
        out = tk.LabelFrame(self, text="Salida / Log", padx=8, pady=8)
        out.place(x=10, y=250, width=740, height=260)
        self.log = scrolledtext.ScrolledText(out, wrap=tk.WORD, state=tk.NORMAL)
        self.log.pack(fill=tk.BOTH, expand=True)
        self.print(f"[Demo] Contraseña de muestra: '{plaintext_demo}' (hash: {hash_text(plaintext_demo, HASH_ALGO)})")
        self.print("[Info] Ajusta 'Alfabeto' y 'Max Len' para una demo rápida. Usa 'Crear wordlist de ejemplo' si no tienes un archivo.")

    def browse_wordlist(self):
        p = filedialog.askopenfilename(title="Selecciona wordlist", filetypes=[("Text files","*.txt"),("All files","*.*")])
        if p:
            self.wordlist_path.set(p)

    def create_sample_wordlist(self):
        path = Path(self.wordlist_path.get())
        try:
            ensure_wordlist(path, create_sample=True)
            messagebox.showinfo("Wordlist creada", f"Se creó un wordlist de ejemplo en:\n{path}")
            self.print(f"[Info] Wordlist de ejemplo creado en: {path}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear el wordlist: {e}")

    def print(self, *args):
        self.log.insert(tk.END, " ".join(str(a) for a in args) + "\\n")
        self.log.see(tk.END)
        self.update_idletasks()

    def run_in_thread(self, target, *args):
        if self.thread and self.thread.is_alive():
            messagebox.showwarning("En ejecución", "Ya hay una operación en ejecución. Deténla antes de iniciar otra.")
            return False
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=target, args=args, daemon=True)
        self.thread.start()
        return True

    def stop_running(self):
        if self.stop_event:
            self.stop_event.set()
            self.print("[Control] Stop solicitado.")
            self.status_var.set("Stopping...")

    def run_dict(self):
        wordlist = Path(self.wordlist_path.get())
        if not wordlist.exists():
            messagebox.showwarning("Wordlist no encontrada", f"No se encontró: {wordlist}\\nPuedes crear una con 'Crear wordlist de ejemplo'.")
            return
        self.status_var.set("Dict running")
        self.print("[Dict] Iniciando ataque por diccionario...")
        target_hash = hash_text(plaintext_demo, HASH_ALGO)
        def job():
            found, t, code = dict_attack(target_hash, wordlist, HASH_ALGO, progress_callback=self.print, stop_event=self.stop_event)
            if code == "NO_WORDLIST":
                self.print("[Dict] Wordlist no existe.")
                self.status_var.set("Idle")
                return
            if code == "STOPPED":
                self.print("[Dict] Detenido por el usuario.")
                self.status_var.set("Idle")
                return
            if found:
                self.print(f"[Dict] ¡Contraseña encontrada! -> '{found}' (tiempo: {t:.4f} s)")
            else:
                self.print(f"[Dict] No encontrada en el diccionario (tiempo: {t:.4f} s)")
            self.status_var.set("Idle")
        self.run_in_thread(job)

    def run_bruteforce(self):
        alphabet = self.alphabet.get()
        max_len = int(self.max_len.get())
        if not alphabet:
            messagebox.showwarning("Alfabeto vacío", "Define el alfabeto para la fuerza bruta.")
            return
        self.status_var.set("Brute running")
        self.print(f"[Brute] Iniciando fuerza bruta (alfabeto len={len(alphabet)}, max_len={max_len})...")
        target_hash = hash_text(plaintext_demo, HASH_ALGO)
        def job():
            found, t, code = brute_force_attack(target_hash, alphabet, max_len, HASH_ALGO, progress_callback=self.print, stop_event=self.stop_event)
            if code == "STOPPED":
                self.print("[Brute] Detenido por el usuario.")
                self.status_var.set("Idle")
                return
            if found:
                self.print(f"[Brute] ¡Contraseña encontrada! -> '{found}' (tiempo: {t:.4f} s)")
            else:
                self.print(f"[Brute] No encontrada con alfabeto='{alphabet}', max_len={max_len} (tiempo: {t:.4f} s)")
            self.status_var.set("Idle")
        self.run_in_thread(job)

if __name__ == "__main__":
    app = CrackingApp()
    app.mainloop()
