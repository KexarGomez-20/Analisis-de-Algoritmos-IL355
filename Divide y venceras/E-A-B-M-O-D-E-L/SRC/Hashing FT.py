# cracking_gui_dyv_benchmark_embed.py
# DEMO EDUCATIVO CON GUI - DyV + Benchmark (gráfica embebida en GUI)
# Implementa DyV y añade un modo de Benchmark que compara Fuerza Bruta secuencial vs DyV.
# Al finalizar el benchmark guarda CSV + PNG y también **muestra la gráfica dentro de la GUI**.
#
# Ejecutar: python cracking_gui_dyv_benchmark_embed.py
#
import hashlib, itertools, time, threading, concurrent.futures, csv
from pathlib import Path
import string
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, Toplevel
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

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

# ---------------- DyV core ----------------
def generate_prefixes(alphabet, prefix_len):
    if prefix_len == 0:
        return ['']
    return [''.join(p) for p in itertools.product(alphabet, repeat=prefix_len)]

def split_round_robin(prefixes, p):
    groups = [[] for _ in range(p)]
    for i, pref in enumerate(prefixes):
        groups[i % p].append(pref)
    return groups

def brute_force_dyv(target_hash, alphabet, max_len, prefix_len, workers, algo="sha256", stop_event=None, progress_callback=None):
    start = time.perf_counter()
    prefixes = generate_prefixes(alphabet, prefix_len)
    if not prefixes:
        prefixes = ['']
    groups = split_round_robin(prefixes, workers or 1)
    manager = threading.Lock()
    shared_result = {"found": None}
    total_checked = [0]

    def worker(pref_list):
        nonlocal shared_result
        for pref in pref_list:
            for length in range(len(pref), max_len+1):
                if stop_event and stop_event.is_set():
                    return
                if length == len(pref):
                    candidate = pref
                    total_checked[0] += 1
                    if progress_callback and total_checked[0] % 5000 == 0:
                        progress_callback(f"[W] Checked {total_checked[0]} candidates (last: {candidate})")
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
                        progress_callback(f"[W] Checked {total_checked[0]} candidates (last: {candidate})")
                    if hash_text(candidate, algo) == target_hash:
                        with manager:
                            shared_result["found"] = candidate
                        if stop_event:
                            stop_event.set()
                        return

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers or 1) as executor:
        futures = []
        for i in range(workers):
            futures.append(executor.submit(worker, groups[i]))
        try:
            for fut in concurrent.futures.as_completed(futures):
                if shared_result["found"]:
                    break
        except KeyboardInterrupt:
            if stop_event:
                stop_event.set()

    elapsed = time.perf_counter() - start
    return shared_result["found"], elapsed, None, total_checked[0]

# ---------------- Sequential brute ----------------
def brute_force_attack(target_hash, alphabet, max_len, algo="sha256", stop_event=None, progress_callback=None):
    start = time.perf_counter()
    total = 0
    for length in range(1, max_len+1):
        for tup in itertools.product(alphabet, repeat=length):
            if stop_event and stop_event.is_set():
                return None, time.perf_counter() - start, "STOPPED", total
            candidate = "".join(tup)
            total += 1
            if progress_callback and total % 5000 == 0:
                progress_callback(f"[BF] Checked {total} candidates (last: {candidate})")
            if hash_text(candidate, algo) == target_hash:
                elapsed = time.perf_counter() - start
                return candidate, elapsed, None, total
    elapsed = time.perf_counter() - start
    return None, elapsed, None, total

# ---------------- Benchmark runner (returns fig) ----------------
def run_benchmark_series_with_figure(out_dir, alphabet, max_len_values, prefix_len, workers_list, trials, target_plain):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    target_hash = hash_text(target_plain, HASH_ALGO)
    rows = []
    for max_len in max_len_values:
        # sequential brute average
        bf_times = []
        bf_checks = []
        for _ in range(trials):
            _, t, _, checks = brute_force_attack(target_hash, alphabet, max_len)
            bf_times.append(t); bf_checks.append(checks)
        avg_bf = sum(bf_times)/len(bf_times)
        avg_bf_checks = sum(bf_checks)/len(bf_checks)
        rows.append(("Brute_Seq", 0, max_len, avg_bf, avg_bf_checks))
        # DyV variants
        for w in workers_list:
            dyv_times = []
            dyv_checks = []
            for _ in range(trials):
                _, t, _, checks = brute_force_dyv(target_hash, alphabet, max_len, prefix_len, w)
                dyv_times.append(t); dyv_checks.append(checks)
            avg_dyv = sum(dyv_times)/len(dyv_times)
            avg_dyv_checks = sum(dyv_checks)/len(dyv_checks)
            rows.append((f"DyV_{w}", w, max_len, avg_dyv, avg_dyv_checks))
    # write CSV
    csv_path = out_dir / "benchmark_results.csv"
    with csv_path.open("w", newline='', encoding='utf-8') as cf:
        writer = csv.writer(cf)
        writer.writerow(["method","workers","max_len","avg_time_s","avg_checks"])
        for r in rows:
            writer.writerow(r)
    # build figure
    fig, ax = plt.subplots(figsize=(8,5))
    methods = sorted(set(r[0] for r in rows))
    for m in methods:
        xs = [r[2] for r in rows if r[0]==m]
        ys = [r[3] for r in rows if r[0]==m]
        if xs and ys:
            ax.plot(xs, ys, marker='o', label=m)
    ax.set_xlabel("max_len (n)")
    ax.set_ylabel("avg time (s)")
    ax.set_title("DyV vs Brute-force (avg over trials)")
    ax.grid(True)
    ax.legend()
    plot_path = out_dir / "benchmark_plot.png"
    fig.savefig(plot_path)
    return csv_path, plot_path, fig

# -------- GUI App --------
class CrackingApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Cracking Demo (GUI) - DyV + Benchmark (Embed Plot)")
        self.geometry("980x680")
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
        cfg = tk.LabelFrame(self, text="Configuración (DyV / Benchmark)", padx=8, pady=8)
        cfg.place(x=10, y=10, width=960, height=180)

        tk.Label(cfg, text="Alfabeto (para DyV):").grid(row=0, column=0, sticky="w")
        tk.Entry(cfg, textvariable=self.alphabet, width=64).grid(row=0, column=1, sticky="w", padx=4)
        tk.Label(cfg, text="Max Len (para DyV):").grid(row=0, column=2, sticky="w")
        tk.Entry(cfg, textvariable=self.max_len, width=6).grid(row=0, column=3, sticky="e", padx=4)

        tk.Label(cfg, text="Prefix len (DyV):").grid(row=1, column=0, sticky="w")
        tk.Entry(cfg, textvariable=self.prefix_len, width=6).grid(row=1, column=1, sticky="w", padx=4)
        tk.Label(cfg, text="Workers (DyV):").grid(row=1, column=2, sticky="w")
        tk.Entry(cfg, textvariable=self.workers, width=6).grid(row=1, column=3, sticky="e", padx=4)

        tk.Label(cfg, text="Benchmark: max_len range (comma separated):").grid(row=2, column=0, sticky="w")
        self.bench_range = tk.StringVar(value="1,2,3,4")
        tk.Entry(cfg, textvariable=self.bench_range, width=30).grid(row=2, column=1, sticky="w", padx=4)
        tk.Label(cfg, text="Workers list (comma separated):").grid(row=2, column=2, sticky="w")
        self.bench_workers = tk.StringVar(value="1,2,4")
        tk.Entry(cfg, textvariable=self.bench_workers, width=20).grid(row=2, column=3, sticky="w", padx=4)
        tk.Label(cfg, text="Trials:").grid(row=3, column=0, sticky="w")
        self.bench_trials = tk.IntVar(value=2)
        tk.Entry(cfg, textvariable=self.bench_trials, width=6).grid(row=3, column=1, sticky="w", padx=4)

        tk.Button(cfg, text="Examinar wordlist (opcional)", command=self.browse_wordlist).grid(row=4, column=0, sticky="w", pady=6)
        tk.Button(cfg, text="Crear wordlist de ejemplo", command=self.create_sample_wordlist).grid(row=4, column=1, sticky="w", pady=6)

        # Middle frame: controls and status
        ctrl = tk.LabelFrame(self, text="Controles", padx=8, pady=8)
        ctrl.place(x=10, y=200, width=960, height=80)

        tk.Button(ctrl, text="Ejecutar DyV (Divide y Vencerás)", command=self.run_dyv).grid(row=0, column=0, padx=6)
        tk.Button(ctrl, text="Detener", command=self.stop_running, fg="red").grid(row=0, column=1, padx=6)
        tk.Button(ctrl, text="Benchmark: Brute vs DyV (embed plot)", command=self.run_benchmark).grid(row=0, column=2, padx=6)
        tk.Label(ctrl, text="Estado:").grid(row=0, column=3, sticky="e")
        tk.Label(ctrl, textvariable=self.status_var, fg="blue").grid(row=0, column=4, sticky="w", padx=4)

        # Bottom frame: log/output
        out = tk.LabelFrame(self, text="Salida / Log", padx=8, pady=8)
        out.place(x=10, y=290, width=960, height=380)
        self.log = scrolledtext.ScrolledText(out, wrap=tk.WORD, state=tk.NORMAL)
        self.log.pack(fill=tk.BOTH, expand=True)
        self.print(f"[Demo] Contraseña de muestra: '{plaintext_demo}' (hash: {hash_text(plaintext_demo, HASH_ALGO)})")
        self.print("[Info] Esta versión implementa DyV y muestra la gráfica del benchmark embebida en la GUI.")
        self.print("[AVISO] Ejecuta solo contra hashes/contraseñas de tu propiedad.")

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
            found, t, code, checks = brute_force_dyv(target_hash, alphabet, max_len, prefix_len, workers, HASH_ALGO, stop_event=self.stop_event, progress_callback=self.print)
            if code == "STOPPED":
                self.print("[DyV] Detenido por el usuario.")
                self.status_var.set("Idle")
                return
            if found:
                self.print(f"[DyV] ¡Contraseña encontrada! -> '{found}' (tiempo: {t:.4f} s) checks={checks}")
            else:
                self.print(f"[DyV] No encontrada con alfabeto='{alphabet}', max_len={max_len}, prefix_len={prefix_len} (tiempo: {t:.4f} s) checks={checks}")
            self.status_var.set("Idle")

        self.run_in_thread(job)

    def run_benchmark(self):
        # parse inputs
        try:
            max_len_values = [int(x.strip()) for x in self.bench_range.get().split(",") if x.strip()]
            workers_list = [int(x.strip()) for x in self.bench_workers.get().split(",") if x.strip()]
            trials = int(self.bench_trials.get())
        except Exception as e:
            messagebox.showerror("Entrada inválida", f"Rango o workers inválidos: {e}")
            return
        alphabet = self.alphabet.get()
        prefix_len = int(self.prefix_len.get())
        if not alphabet:
            messagebox.showwarning("Alfabeto vacío", "Define el alfabeto para benchmarking.")
            return
        # warn about potential long runs
        est = len(alphabet) ** max(max_len_values)
        if est > 1000000 and not messagebox.askyesno("Advertencia", f"El keyspace estimado es ~{est} candidatos. Esto puede tardar. ¿Continuar?"):
            return
        self.status_var.set("Benchmark running")
        self.print(f"[Benchmark] Iniciando benchmark (alphabet len={len(alphabet)}, max_len={max_len_values}, prefix_len={prefix_len}, workers={workers_list}, trials={trials})...")

        def job():
            try:
                csv_path, plot_path, fig = run_benchmark_series_with_figure(Path(__file__).resolve().parent, alphabet, max_len_values, prefix_len, workers_list, trials, plaintext_demo)
                self.print(f"[Benchmark] Guardado CSV: {csv_path}")
                self.print(f"[Benchmark] Guardado gráfico: {plot_path}")
                # show figure embedded in GUI
                self.show_figure_in_toplevel(fig)
                messagebox.showinfo("Benchmark completado", f"CSV: {csv_path}\\nPNG: {plot_path}")
            except Exception as e:
                self.print(f"[Benchmark] Error: {e}")
                messagebox.showerror("Benchmark error", str(e))
            finally:
                self.status_var.set("Idle")

        self.run_in_thread(job)

    def show_figure_in_toplevel(self, fig):
        # Create a Toplevel window and embed the Matplotlib figure using FigureCanvasTkAgg
        top = Toplevel(self)
        top.title("Benchmark plot (embedded)")
        top.geometry("820x520")
        canvas = FigureCanvasTkAgg(fig, master=top)
        canvas.draw()
        widget = canvas.get_tk_widget()
        widget.pack(fill=tk.BOTH, expand=True)

    # rest omitted for brevity (but present in file)
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
            found, t, code, checks = brute_force_dyv(target_hash, alphabet, max_len, prefix_len, workers, HASH_ALGO, stop_event=self.stop_event, progress_callback=self.print)
            if code == "STOPPED":
                self.print("[DyV] Detenido por el usuario.")
                self.status_var.set("Idle")
                return
            if found:
                self.print(f"[DyV] ¡Contraseña encontrada! -> '{found}' (tiempo: {t:.4f} s) checks={checks}")
            else:
                self.print(f"[DyV] No encontrada con alfabeto='{alphabet}', max_len={max_len}, prefix_len={prefix_len} (tiempo: {t:.4f} s) checks={checks}")
            self.status_var.set("Idle")

        self.run_in_thread(job)

if __name__ == "__main__":
    app = CrackingApp()
    app.mainloop()
