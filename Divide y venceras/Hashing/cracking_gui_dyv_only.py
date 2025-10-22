# cracking_gui_dyv_only.py
# DEMO EDUCATIVO CON GUI - Divide y Vencerás (DyV) (Versión solo DyV)
# USAR SOLO CON CONTRASEÑAS/HASHES QUE POSEAS. NO USAR CONTRA SISTEMAS AJENOS.
#
# Ejecutar: python cracking_gui_dyv_only.py
#
import hashlib, itertools, time, threading, concurrent.futures
from pathlib import Path
import string
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

# ---------------- CONFIG ----------------
plaintext_demo = "s3c"  # contraseña de ejemplo para generar el hash (educativo)
HASH_ALGO = "sha256"
DEFAULT_ALPHABET = string.ascii_lowercase + string.digits
DEFAULT_MAX_LEN = 4
DEFAULT_PREFIX_LEN = 1
DEFAULT_WORKERS = 4
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
        sample = ["password","123456","admin","letmein","qwerty","s3c","welcome","usuario","contraseña"]
        path.write_text("\\n".join(sample), encoding="utf-8")
        return True
    return False

# ---------------- DyV core (solo DyV) ----------------
def generate_prefixes(alphabet, prefix_len):
    if prefix_len == 0:
        return ['']
    return [''.join(p) for p in itertools.product(alphabet, repeat=prefix_len)]

def split_round_robin(prefixes, p):
    groups = [[] for _ in range(p)]
    for i, pref in enumerate(prefixes):
        groups[i % p].append(pref)
    return groups

def brute_force_dyv(target_hash, alphabet, max_len, prefix_len, workers, algo="sha256", progress_callback=None, stop_event=None):
    """
    Implementación DyV (solo DyV).
    Divide: generar prefijos de longitud prefix_len.
    Vencer: cada worker explora candidatos que empiezan por sus prefijos.
    Combinar: si un worker encuentra la contraseña, setear stop_event y retornar resultado.
    """
    start = time.time()
    prefixes = generate_prefixes(alphabet, prefix_len)
    if not prefixes:
        prefixes = ['']
    groups = split_round_robin(prefixes, workers or 1)
    manager = threading.Lock()
    shared_result = {"found": None}
    total_checked = [0]  # mutable counter

    def worker(pref_list, wid):
        nonlocal shared_result
        for pref in pref_list:
            for length in range(len(pref), max_len+1):
                if stop_event and stop_event.is_set():
                    return
                if length == len(pref):
                    candidate = pref
                    total_checked[0] += 1
                    if progress_callback and total_checked[0] % 5000 == 0:
                        progress_callback(f"[W{wid}] Checked {total_checked[0]} candidates (last: {candidate})")
                    if hash_text(candidate, algo) == target_hash:
                        with manager:
                            shared_result["found"] = candidate
                        if stop_event:
                            stop_event.set()
                        return
                    continue
                for suf in itertools.product(alphabet, repeat=length - len(pref)):
                    if stop_event and stop_event.is_set():
                        return
                    candidate = pref + ''.join(suf)
                    total_checked[0] += 1
                    if progress_callback and total_checked[0] % 5000 == 0:
                        progress_callback(f"[W{wid}] Checked {total_checked[0]} candidates (last: {candidate})")
                    if hash_text(candidate, algo) == target_hash:
                        with manager:
                            shared_result["found"] = candidate
                        if stop_event:
                            stop_event.set()
                        return

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers or 1) as executor:
        futures = []
        for i in range(workers):
            futures.append(executor.submit(worker, groups[i], i+1))
        try:
            for fut in concurrent.futures.as_completed(futures):
                if shared_result["found"]:
                    break
        except KeyboardInterrupt:
            if stop_event:
                stop_event.set()

    elapsed = time.time() - start
    return shared_result["found"], elapsed, None

# -------- GUI App (DyV only) --------
class CrackingApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Cracking Demo (GUI) - DyV (Solo)")
        self.geometry("820x520")
        self.resizable(False, False)

        # Variables
        self.wordlist_path = tk.StringVar(value=str(Path(__file__).resolve().parent / DEFAULT_WORDLIST_NAME))
        self.alphabet = tk.StringVar(value=DEFAULT_ALPHABET)
        self.max_len = tk.IntVar(value=DEFAULT_MAX_LEN)
        self.prefix_len = tk.IntVar(value=DEFAULT_PREFIX_LEN)
        self.workers = tk.IntVar(value=DEFAULT_WORKERS)
        self.status_var = tk.StringVar(value="Idle")
        self.stop_event = None
        self.thread = None

        # Top frame: configuration
        cfg = tk.LabelFrame(self, text="Configuración (DyV)", padx=8, pady=8)
        cfg.place(x=10, y=10, width=800, height=150)

        tk.Label(cfg, text="Alfabeto (para DyV):").grid(row=0, column=0, sticky="w")
        tk.Entry(cfg, textvariable=self.alphabet, width=60).grid(row=0, column=1, sticky="w", padx=4)
        tk.Label(cfg, text="Max Len:").grid(row=0, column=2, sticky="w")
        tk.Entry(cfg, textvariable=self.max_len, width=6).grid(row=0, column=2, sticky="e", padx=4)

        tk.Label(cfg, text="Prefix len (DyV):").grid(row=1, column=0, sticky="w")
        tk.Entry(cfg, textvariable=self.prefix_len, width=6).grid(row=1, column=1, sticky="w", padx=4)
        tk.Label(cfg, text="Workers:").grid(row=1, column=2, sticky="w")
        tk.Entry(cfg, textvariable=self.workers, width=6).grid(row=1, column=2, sticky="e", padx=4)

        tk.Button(cfg, text="Examinar wordlist (opcional)", command=self.browse_wordlist).grid(row=2, column=0, sticky="w", pady=6)
        tk.Button(cfg, text="Crear wordlist de ejemplo", command=self.create_sample_wordlist).grid(row=2, column=1, sticky="w", pady=6)

        # Middle frame: controls and status
        ctrl = tk.LabelFrame(self, text="Controles", padx=8, pady=8)
        ctrl.place(x=10, y=170, width=800, height=70)

        tk.Button(ctrl, text="Ejecutar DyV (Divide y Vencerás)", command=self.run_dyv).grid(row=0, column=0, padx=6)
        tk.Button(ctrl, text="Detener", command=self.stop_running, fg="red").grid(row=0, column=1, padx=6)
        tk.Label(ctrl, text="Estado:").grid(row=0, column=2, sticky="e")
        tk.Label(ctrl, textvariable=self.status_var, fg="blue").grid(row=0, column=3, sticky="w", padx=4)

        # Bottom frame: log/output
        out = tk.LabelFrame(self, text="Salida / Log", padx=8, pady=8)
        out.place(x=10, y=250, width=800, height=260)
        self.log = scrolledtext.ScrolledText(out, wrap=tk.WORD, state=tk.NORMAL)
        self.log.pack(fill=tk.BOTH, expand=True)
        self.print(f"[Demo] Contraseña de muestra: '{plaintext_demo}' (hash: {hashlib.new(HASH_ALGO, plaintext_demo.encode()).hexdigest()})")
        self.print("[Info] Esta versión implementa únicamente Divide y Vencerás (DyV).")
        self.print("[AVISO] Ejecuta solo contra hashes/contraseñas de tu propiedad. Esto es una demo educativa.")

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

    def run_dyv(self):
        alphabet = self.alphabet.get()
        max_len = int(self.max_len.get())
        prefix_len = int(self.prefix_len.get())
        workers = int(self.workers.get())
        if not alphabet:
            messagebox.showwarning("Alfabeto vacío", "Define el alfabeto para DyV.")
            return
        if prefix_len < 0:
            messagebox.showwarning("Prefix len inválido", "Prefix len debe ser >= 0.")
            return
        if workers <= 0:
            messagebox.showwarning("Workers inválidos", "Workers debe ser >= 1.")
            return
        approx_prefixes = len(alphabet) ** prefix_len
        if approx_prefixes > 10000 and workers < 2:
            if not messagebox.askyesno("Advertencia", f"Se generarán ~{approx_prefixes} prefijos (prefix_len={prefix_len}). ¿Deseas continuar?"):
                return
        self.status_var.set("DyV running")
        self.print(f"[DyV] Iniciando DyV (alphabet len={len(alphabet)}, max_len={max_len}, prefix_len={prefix_len}, workers={workers})...")
        target_hash = hash_text(plaintext_demo, HASH_ALGO)

        def job():
            found, t, code = brute_force_dyv(target_hash, alphabet, max_len, prefix_len, workers, HASH_ALGO, progress_callback=self.print, stop_event=self.stop_event)
            if code == "STOPPED":
                self.print("[DyV] Detenido por el usuario.")
                self.status_var.set("Idle")
                return
            if found:
                self.print(f"[DyV] ¡Contraseña encontrada! -> '{found}' (tiempo: {t:.4f} s)")
            else:
                self.print(f"[DyV] No encontrada con alfabeto='{alphabet}', max_len={max_len}, prefix_len={prefix_len} (tiempo: {t:.4f} s)")
            self.status_var.set("Idle")

        self.run_in_thread(job)

if __name__ == "__main__":
    app = CrackingApp()
    app.mainloop()
