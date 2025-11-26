"""
Versión mejorada de la GUI:
 - Generar contraseña aleatoria (solo muestra hash)
 - Muestra complejidades teóricas y empíricas
 - Dibuja MST (PRIM) en una ventana con tkinter.Canvas (sin librerías externas)
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import threading
import time
import math
import heapq
import itertools
import hashlib
import random
from collections import Counter, deque
from typing import Optional, Tuple, List, Dict, Generator, Set

#Configuraciones por defecto
WORDLIST_PATH = "wordlist.txt"
DEFAULT_ALPHABET = "abcdefghijklmnopqrstuvwxyz0123456789"
DEFAULT_MAX_LEN = 4
DEFAULT_HASH = "sha256"

#Funciones auxiliares
def hash_text(text: str, algo: str = "sha256") -> str:
    h = hashlib.new(algo)
    h.update(text.encode('utf-8'))
    return h.hexdigest()

def load_wordlist(path: str) -> List[str]:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return []

def levenshtein(a: str, b: str) -> int:
    if a == b:
        return 0
    la, lb = len(a), len(b)
    if la == 0:
        return lb
    if lb == 0:
        return la
    prev = list(range(lb + 1))
    cur = [0] * (lb + 1)
    for i in range(1, la + 1):
        cur[0] = i
        ai = a[i - 1]
        for j in range(1, lb + 1):
            cost = 0 if ai == b[j - 1] else 1
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + cost)
        prev, cur = cur, prev
    return prev[lb]

#Metodos de ataque
def attack_bruteforce(target_hash: str, alphabet: str, max_len: int, algo: str,
                      progress_callback=None, stop_flag: threading.Event=None,
                      candidate_limit: Optional[int]=None) -> Tuple[Optional[str], float, int]:
    start = time.perf_counter()
    checks = 0
    for L in range(1, max_len + 1):
        for tup in itertools.product(alphabet, repeat=L):
            if stop_flag and stop_flag.is_set():
                return None, time.perf_counter() - start, checks
            checks += 1
            if candidate_limit and checks > candidate_limit:
                return None, time.perf_counter() - start, checks
            candidate = ''.join(tup)
            if progress_callback and checks % 5000 == 0:
                progress_callback(f"[FB] checked {checks} candidates (last: {candidate})")
            if hash_text(candidate, algo) == target_hash:
                return candidate, time.perf_counter() - start, checks
    return None, time.perf_counter() - start, checks

def dyv_generate_of_length(alphabet: str, length: int) -> List[str]:
    if length == 0:
        return [""]
    if length == 1:
        return [c for c in alphabet]
    k = length // 2
    left = dyv_generate_of_length(alphabet, k)
    right = dyv_generate_of_length(alphabet, length - k)
    result = []
    for a in left:
        for b in right:
            result.append(a + b)
    return result
 
#Divide y Venceras
def attack_dyv(target_hash: str, alphabet: str, max_len: int, algo: str,
               progress_callback=None, stop_flag: threading.Event=None,
               candidate_limit: Optional[int]=None) -> Tuple[Optional[str], float, int]:
    start = time.perf_counter()
    checks = 0
    for L in range(1, max_len + 1):
        candidates = dyv_generate_of_length(alphabet, L)
        for c in candidates:
            if stop_flag and stop_flag.is_set():
                return None, time.perf_counter() - start, checks
            checks += 1
            if candidate_limit and checks > candidate_limit:
                return None, time.perf_counter() - start, checks
            if progress_callback and checks % 5000 == 0:
                progress_callback(f"[DyV] checked {checks} candidates (len={L}, last={c})")
            if hash_text(c, algo) == target_hash:
                return c, time.perf_counter() - start, checks
    return None, time.perf_counter() - start, checks

def generate_edits_bfs(seed: str, alphabet: str, max_edits: int) -> Generator[str, None, None]:
    from collections import deque
    seen: Set[str] = set([seed])
    dq = deque([(seed, 0)])
    while dq:
        s, d = dq.popleft()
        if d > 0:
            yield s
        if d >= max_edits:
            continue
        for i in range(len(s)):
            for c in alphabet:
                if s[i] == c:
                    continue
                ns = s[:i] + c + s[i+1:]
                if ns not in seen:
                    seen.add(ns)
                    dq.append((ns, d+1))
        for i in range(len(s)+1):
            for c in alphabet:
                ns = s[:i] + c + s[i:]
                if ns not in seen:
                    seen.add(ns)
                    dq.append((ns, d+1))
        if len(s) > 0:
            for i in range(len(s)):
                ns = s[:i] + s[i+1:]
                if ns not in seen:
                    seen.add(ns)
                    dq.append((ns, d+1))
                 
#Programación dinamica 
def attack_prog_dinamica_edits(target_hash: str, wordlist_path: str, alphabet: str, max_edits: int,
                               algo: str, progress_callback=None, stop_flag: threading.Event=None,
                               per_seed_limit: Optional[int]=None, global_limit: Optional[int]=None) -> Tuple[Optional[str], float, int]:
    start = time.perf_counter()
    words = load_wordlist(wordlist_path)
    if not words:
        return None, time.perf_counter() - start, 0
    counts = Counter(words)
    ordered = sorted(list(dict.fromkeys(words)), key=lambda w: (-counts[w], w))
    checks = 0
    for seed in ordered:
        if stop_flag and stop_flag.is_set():
            return None, time.perf_counter() - start, checks
        local = 0
        for cand in generate_edits_bfs(seed, alphabet, max_edits):
            if stop_flag and stop_flag.is_set():
                return None, time.perf_counter() - start, checks
            checks += 1
            local += 1
            if per_seed_limit and local > per_seed_limit:
                break
            if global_limit and checks > global_limit:
                return None, time.perf_counter() - start, checks
            if progress_callback and checks % 2000 == 0:
                progress_callback(f"[ProgDin] checked {checks} candidates (seed={seed} last={cand})")
            if hash_text(cand, algo) == target_hash:
                return cand, time.perf_counter() - start, checks
    return None, time.perf_counter() - start, checks

#Voraz (Prim)
def build_knn_graph(words: List[str], k: int = 8) -> Dict[int, List[Tuple[int, int]]]:
    n = len(words)
    adj = {i: [] for i in range(n)}
    for i in range(n):
        dists = []
        for j in range(n):
            if i == j:
                continue
            d = levenshtein(words[i], words[j])
            dists.append((d, j))
        dists.sort(key=lambda x: x[0])
        for d, j in dists[:k]:
            adj[i].append((j, d))
    return adj

def prim_mst(adj: Dict[int, List[Tuple[int,int]]], start: int = 0) -> List[Tuple[int,int,int]]:
    n = len(adj)
    if n == 0:
        return []
    visited = set()
    mst_edges = []
    heap = []
    visited.add(start)
    for v, w in adj[start]:
        heapq.heappush(heap, (w, start, v))
    while heap and len(visited) < n:
        w, u, v = heapq.heappop(heap)
        if v in visited:
            continue
        visited.add(v)
        mst_edges.append((u, v, w))
        for nbr, ww in adj[v]:
            if nbr not in visited:
                heapq.heappush(heap, (ww, v, nbr))
    if len(visited) < n:
        for node in range(n):
            if node not in visited:
                visited.add(node)
                for v, w in adj[node]:
                    heapq.heappush(heap, (w, node, v))
                while heap and len(visited) < n:
                    w, u, v = heapq.heappop(heap)
                    if v in visited:
                        continue
                    visited.add(v)
                    mst_edges.append((u, v, w))
                    for nbr, ww in adj[v]:
                        if nbr not in visited:
                            heapq.heappush(heap, (ww, v, nbr))
    return mst_edges

def mst_to_order(words: List[str], mst_edges: List[Tuple[int,int,int]], start_nodes: Optional[List[int]] = None) -> List[str]:
    n = len(words)
    tree = {i: [] for i in range(n)}
    for u, v, w in mst_edges:
        tree[u].append(v)
        tree[v].append(u)
    if start_nodes is None or not start_nodes:
        start_nodes = [0]
    seen = set()
    order = []
    for s in start_nodes:
        if s in seen:
            continue
        dq = deque([s])
        seen.add(s)
        while dq:
            u = dq.popleft()
            order.append(words[u])
            for v in tree[u]:
                if v not in seen:
                    seen.add(v)
                    dq.append(v)
    for i in range(n):
        if i not in seen:
            order.append(words[i])
    return order

def attack_voraz_prim(target_hash: str, wordlist_path: str, k_neighbors: int, start_top_n: int,
                      algo: str, progress_callback=None, stop_flag: threading.Event=None,
                      progress_every: int = 2000, global_limit: Optional[int]=None) -> Tuple[Optional[str], float, int]:
    start = time.perf_counter()
    words = load_wordlist(wordlist_path)
    if not words:
        return None, time.perf_counter() - start, 0
    cnt = Counter(words)
    unique_words = list(dict.fromkeys(words))
    top = [w for w, _ in cnt.most_common(start_top_n)]
    first_index = {w: i for i, w in enumerate(unique_words)}
    start_nodes = [first_index[w] for w in top if w in first_index]
    adj = build_knn_graph(unique_words, k=k_neighbors)
    mst_edges = prim_mst(adj, start=0)
    order = mst_to_order(unique_words, mst_edges, start_nodes=start_nodes)
    checks = 0
    for w in order:
        if stop_flag and stop_flag.is_set():
            return None, time.perf_counter() - start, checks
        checks += 1
        if global_limit and checks > global_limit:
            return None, time.perf_counter() - start, checks
        if progress_callback and checks % progress_every == 0:
            progress_callback(f"[Prim] checked {checks} candidates (last={w})")
        if hash_text(w, algo) == target_hash:
            return w, time.perf_counter() - start, checks
    return None, time.perf_counter() - start, checks

# MST visual (tkinter Canvas)
def compute_mst_for_visual(wordlist_path: str, k_neighbors: int = 6, top_n: int = 200):
    words = load_wordlist(wordlist_path)
    if not words:
        return [], [], []
    cnt = Counter(words)
    unique = list(dict.fromkeys(words))
    if len(unique) > top_n:
        top_words = [w for w, _ in cnt.most_common(top_n)]
        chosen = []
        for w in top_words:
            if w in unique and w not in chosen:
                chosen.append(w)
        i = 0
        while len(chosen) < top_n and i < len(unique):
            if unique[i] not in chosen:
                chosen.append(unique[i])
            i += 1
        subset = chosen
    else:
        subset = unique[:top_n]
    idx_map = {w: i for i, w in enumerate(subset)}
    adj = {i: [] for i in range(len(subset))}
    for i, wi in enumerate(subset):
        dists = []
        for j, wj in enumerate(subset):
            if i == j: continue
            d = levenshtein(wi, wj)
            dists.append((d, j))
        dists.sort(key=lambda x: x[0])
        for d, j in dists[:k_neighbors]:
            adj[i].append((j, d))
    mst_edges = prim_mst(adj, start=0)
    cnt_subset = Counter([w for w in words if w in subset])
    top_in_subset = [w for w,_ in cnt_subset.most_common(3)]
    start_indices = [idx_map[w] for w in top_in_subset if w in idx_map]
    return subset, mst_edges, start_indices

def layout_tree_radial(n_nodes: int, mst_edges: List[Tuple[int,int,float]], start_index: int = 0, width=1000, height=700):
    tree = {i: [] for i in range(n_nodes)}
    for u, v, w in mst_edges:
        tree[u].append(v)
        tree[v].append(u)
    from collections import deque
    levels = {}
    seen = set([start_index])
    q = deque([(start_index, 0)])
    max_level = 0
    level_nodes = {}
    while q:
        u, lvl = q.popleft()
        levels[u] = lvl
        level_nodes.setdefault(lvl, []).append(u)
        max_level = max(max_level, lvl)
        for v in tree[u]:
            if v not in seen:
                seen.add(v)
                q.append((v, lvl + 1))
    cx, cy = width // 2, height // 2
    positions = {}
    for lvl in range(max_level + 1):
        nodes = level_nodes.get(lvl, [])
        if not nodes:
            continue
        radius = 40 + (min(width, height) // 2 - 60) * (lvl / max(1, max_level))
        m = len(nodes)
        for k, node in enumerate(nodes):
            theta = 2 * math.pi * k / max(1, m)
            x = cx + int(radius * math.cos(theta))
            y = cy + int(radius * math.sin(theta))
            positions[node] = (x, y)
    for i in range(n_nodes):
        if i not in positions:
            positions[i] = (50 + (i % 10) * 60, height - 50 - (i // 10) * 40)
    return positions

def show_mst_canvas(words_subset: List[str], mst_edges: List[Tuple[int,int,float]], start_indices: List[int], title="MST Visualization"):
    if not words_subset or not mst_edges:
        messagebox.showinfo("MST Visual", "No hay datos para visualizar (subconjunto vacío o sin aristas).")
        return
    n = len(words_subset)
    W, H = 1000, 700
    positions = layout_tree_radial(n, mst_edges, start_index=start_indices[0] if start_indices else 0, width=W, height=H)
    win = tk.Toplevel()
    win.title(title)
    canvas = tk.Canvas(win, width=W, height=H, bg="white")
    canvas.pack(fill="both", expand=True)
    node_radius = 14
    #draw edges
    for u, v, w in mst_edges:
        x1, y1 = positions[u]
        x2, y2 = positions[v]
        canvas.create_line(x1, y1, x2, y2, fill="#999", width=1)
    #Proceso de creación de nodos
    node_items = {}
    for i, w in enumerate(words_subset):
        x, y = positions[i]
        color = "#66c2a5" if i in start_indices else "#8da0cb"
        item = canvas.create_oval(x-node_radius, y-node_radius, x+node_radius, y+node_radius, fill=color, outline="#333")
        text_item = canvas.create_text(x, y, text=str(i), fill="white", font=("Arial", 9))
        node_items[item] = i
        #Adjunta etiqueta para hacer click
        def make_onclick(idx):
            def on_click(event):
                messagebox.showinfo("Node info", f"Index: {idx}\nWord: {words_subset[idx]}")
            return on_click
        canvas.tag_bind(item, "<Button-1>", make_onclick(i))
        canvas.tag_bind(text_item, "<Button-1>", make_onclick(i))
    #leyende
    canvas.create_rectangle(10, 10, 220, 60, fill="#f8f8f8", outline="#ccc")
    canvas.create_oval(20-8, 25-8, 20+8, 25+8, fill="#66c2a5")
    canvas.create_text(45, 25, anchor="w", text="Start nodes (top freq)", font=("Arial", 9))
    canvas.create_oval(20-8, 45-8, 20+8, 45+8, fill="#8da0cb")
    canvas.create_text(45, 45, anchor="w", text="Other nodes", font=("Arial", 9))

#GUI
class CrackerGUI:
    def __init__(self, root):
        self.root = root
        root.title("Cracking Modes - Demo académico (v2)")
        self.stop_flag = threading.Event()
        self.thread = None
        self._secret_plain = None  # almacena contraseña generada (oculta) si se usa generación aleatoria

        main = ttk.Frame(root, padding=8)
        main.grid(row=0, column=0, sticky="nsew")

        ttk.Label(main, text="Target (plain o hash):").grid(row=0, column=0, sticky="w")
        self.target_entry = ttk.Entry(main, width=60)
        self.target_entry.grid(row=0, column=1, columnspan=3, sticky="we")
        ttk.Label(main, text="(si pones texto plano, selecciona 'plain' checkbox)").grid(row=1, column=1, columnspan=3, sticky="w")
        self.is_plain = tk.BooleanVar(value=True)
        ttk.Checkbutton(main, text="plain", variable=self.is_plain).grid(row=0, column=4, sticky="w")

        ttk.Label(main, text="Hash:").grid(row=2, column=0, sticky="w")
        self.hash_combo = ttk.Combobox(main, values=["md5", "sha1", "sha256"], width=8)
        self.hash_combo.set(DEFAULT_HASH)
        self.hash_combo.grid(row=2, column=1, sticky="w")

        ttk.Label(main, text="Modo:").grid(row=3, column=0, sticky="w")
        self.mode_var = tk.StringVar(value="FB")
        modes = [("Fuerza Bruta (FB)", "FB"),
                 ("DyV (Divide & Vencerás)", "DyV"),
                 ("Prog Dinámica (edits desde wordlist)", "PD"),
                 ("Voraz (Prim + MST)", "PRIM")]
        r = 3
        c = 1
        for label, val in modes:
            ttk.Radiobutton(main, text=label, variable=self.mode_var, value=val).grid(row=r, column=c, sticky="w")
            c += 1

        ttk.Label(main, text="Wordlist:").grid(row=4, column=0, sticky="w")
        self.wordlist_entry = ttk.Entry(main, width=50)
        self.wordlist_entry.insert(0, WORDLIST_PATH)
        self.wordlist_entry.grid(row=4, column=1, columnspan=3, sticky="we")
        ttk.Button(main, text="Browse", command=self.browse_wordlist).grid(row=4, column=4)

        ttk.Label(main, text="Alphabet:").grid(row=5, column=0, sticky="w")
        self.alphabet_entry = ttk.Entry(main, width=40)
        self.alphabet_entry.insert(0, DEFAULT_ALPHABET)
        self.alphabet_entry.grid(row=5, column=1, columnspan=3, sticky="we")

        ttk.Label(main, text="Max len (FB/DyV):").grid(row=6, column=0, sticky="w")
        self.maxlen_spin = tk.Spinbox(main, from_=1, to=8, width=5)
        self.maxlen_spin.delete(0, "end"); self.maxlen_spin.insert(0, str(DEFAULT_MAX_LEN))
        self.maxlen_spin.grid(row=6, column=1, sticky="w")

        ttk.Label(main, text="PD: max edits:").grid(row=6, column=2, sticky="w")
        self.pd_edits_spin = tk.Spinbox(main, from_=1, to=3, width=5)
        self.pd_edits_spin.delete(0, "end"); self.pd_edits_spin.insert(0, "2")
        self.pd_edits_spin.grid(row=6, column=3, sticky="w")

        ttk.Label(main, text="Prim: k-neighbors:").grid(row=7, column=0, sticky="w")
        self.prim_k_spin = tk.Spinbox(main, from_=1, to=20, width=5)
        self.prim_k_spin.delete(0, "end"); self.prim_k_spin.insert(0, "6")
        self.prim_k_spin.grid(row=7, column=1, sticky="w")

        ttk.Label(main, text="Prim: top N start:").grid(row=7, column=2, sticky="w")
        self.prim_top_spin = tk.Spinbox(main, from_=1, to=20, width=5)
        self.prim_top_spin.delete(0, "end"); self.prim_top_spin.insert(0, "3")
        self.prim_top_spin.grid(row=7, column=3, sticky="w")

        ttk.Label(main, text="Candidate limit (global, 0 = no limit):").grid(row=8, column=0, sticky="w")
        self.limit_entry = ttk.Entry(main, width=12); self.limit_entry.insert(0, "0"); self.limit_entry.grid(row=8, column=1, sticky="w")

        #Genetador de contraseñas aleatorias
        ttk.Label(main, text="Random pwd len:").grid(row=8, column=2, sticky="w")
        self.random_len_spin = tk.Spinbox(main, from_=3, to=12, width=5)
        self.random_len_spin.delete(0, "end"); self.random_len_spin.insert(0, "6")
        self.random_len_spin.grid(row=8, column=3, sticky="w")
        ttk.Button(main, text="Generar contraseña aleatoria (oculta)", command=self.generate_random_password).grid(row=9, column=1, sticky="we")

        self.start_btn = ttk.Button(main, text="Start", command=self.start_attack); self.start_btn.grid(row=10, column=1, sticky="we")
        self.stop_btn = ttk.Button(main, text="Stop", command=self.stop_attack, state="disabled"); self.stop_btn.grid(row=10, column=2, sticky="we")
        self.load_btn = ttk.Button(main, text="Cargar wordlist (preview)", command=self.preview_wordlist); self.load_btn.grid(row=10, column=3, sticky="we")

        self.output = scrolledtext.ScrolledText(main, width=100, height=20)
        self.output.grid(row=11, column=0, columnspan=5, pady=8)

        root.columnconfigure(0, weight=1); root.rowconfigure(0, weight=1)
        main.columnconfigure(1, weight=1); main.columnconfigure(2, weight=1); main.columnconfigure(3, weight=1)

    def browse_wordlist(self):
        path = filedialog.askopenfilename(title="Select wordlist", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if path:
            self.wordlist_entry.delete(0, "end"); self.wordlist_entry.insert(0, path)

    def preview_wordlist(self):
        path = self.wordlist_entry.get()
        words = load_wordlist(path)
        if not words:
            messagebox.showwarning("Wordlist", "No se pudo cargar la wordlist o está vacía.")
            return
        preview = "\n".join(words[:50])
        self.append_output(f"--- Preview (first 50) ---\n{preview}\n--- total: {len(words)} words ---")

    def append_output(self, text: str):
        self.output.insert("end", f"{text}\n"); self.output.see("end")

    def stop_attack(self):
        self.append_output("[GUI] Stop requested..."); self.stop_flag.set(); self.stop_btn.config(state="disabled")

    def generate_random_password(self):
        length = int(self.random_len_spin.get())
        alphabet = self.alphabet_entry.get()
        pwd = ''.join(random.choice(alphabet) for _ in range(length))
        self._secret_plain = pwd  # almacenarla internamente (oculta)
        # poner solo hash en target y desmarcar 'plain'
        algo = self.hash_combo.get()
        h = hash_text(pwd, algo)
        self.target_entry.delete(0, "end"); self.target_entry.insert(0, h)
        self.is_plain.set(False)
        self.append_output(f"[GUI] Generated random password (hidden). Hash ({algo}): {h}")

    def start_attack(self):
        if self.thread and self.thread.is_alive():
            messagebox.showinfo("Info", "Ya hay una tarea en ejecución. Primero deténla."); return
        target_raw = self.target_entry.get().strip()
        if not target_raw:
            messagebox.showwarning("Input", "Escribe target (texto plano o hash)."); return
        algo = self.hash_combo.get()
        is_plain = self.is_plain.get()
        if is_plain:
            target_hash = hash_text(target_raw, algo)
            self.append_output(f"[GUI] Target plain -> {target_raw} (hash {algo}: {target_hash})")
        else:
            target_hash = target_raw
            self.append_output(f"[GUI] Target hash provided: {target_hash}")
        alphabet = self.alphabet_entry.get()
        try:
            max_len = int(self.maxlen_spin.get())
        except:
            max_len = DEFAULT_MAX_LEN
        try:
            pd_edits = int(self.pd_edits_spin.get())
        except:
            pd_edits = 2
        try:
            prim_k = int(self.prim_k_spin.get())
        except:
            prim_k = 6
        try:
            prim_top = int(self.prim_top_spin.get())
        except:
            prim_top = 3
        try:
            global_limit = int(self.limit_entry.get()); global_limit = None if global_limit <= 0 else global_limit
        except:
            global_limit = None
        mode = self.mode_var.get()
        self.stop_flag.clear(); self.stop_btn.config(state="normal"); self.start_btn.config(state="disabled")
        self.append_output(f"[GUI] Starting mode {mode}...")
        def worker():
            try:
                found = None; elapsed = 0; checks = 0; method = mode
                t0 = time.perf_counter()
                if mode == "FB":
                    self.append_output("[GUI] Running Fuerza Bruta...")
                    found, elapsed, checks = attack_bruteforce(target_hash, alphabet, max_len, algo,
                                                               progress_callback=self.append_output, stop_flag=self.stop_flag,
                                                               candidate_limit=global_limit)
                    method = "FB"
                elif mode == "DyV":
                    self.append_output("[GUI] Running DyV...")
                    found, elapsed, checks = attack_dyv(target_hash, alphabet, max_len, algo,
                                                        progress_callback=self.append_output, stop_flag=self.stop_flag,
                                                        candidate_limit=global_limit)
                    method = "DyV"
                elif mode == "PD":
                    self.append_output("[GUI] Running Prog Dinámica (edits)...")
                    found, elapsed, checks = attack_prog_dinamica_edits(target_hash, self.wordlist_entry.get(),
                                                                        alphabet, pd_edits, algo,
                                                                        progress_callback=self.append_output,
                                                                        stop_flag=self.stop_flag, global_limit=global_limit,
                                                                        per_seed_limit=5000)
                    method = "ProgDin"
                elif mode == "PRIM":
                    self.append_output("[GUI] Running Voraz (Prim + MST)...")
                    found, elapsed, checks = attack_voraz_prim(target_hash, self.wordlist_entry.get(),
                                                              prim_k, prim_top, algo,
                                                              progress_callback=self.append_output,
                                                              stop_flag=self.stop_flag, global_limit=global_limit)
                    method = "PrimMST"
                else:
                    self.append_output("[GUI] Modo no reconocido."); return
                t_total = time.perf_counter() - t0
                if found:
                    self.append_output(f"[RESULT] Found password: {found}  (method={method}) time={elapsed:.4f}s checks={checks}")
                    #si la contraseña fue generada aleatoriamente, revelar (opcional)
                    if self._secret_plain:
                        if found == self._secret_plain:
                            self.append_output(f"[INFO] Coincide con contraseña generada (hidden).")
                else:
                    self.append_output(f"[RESULT] No encontrado (method={method}) time={elapsed:.4f}s checks={checks}")
                #mostrar estadísticas y complejidad teórica/empírica
                time_per_candidate = (elapsed / checks) if checks > 0 else float('inf')
                self.append_output(f"[STATS] Time total: {t_total:.4f}s | Algorithm time: {elapsed:.4f}s | Checks: {checks} | Time/check: {time_per_candidate:.6e}s")
                #complejidad teórica
                if method == "FB":
                    t_theory = "O(k^n)"; s_theory = "O(1) (o O(n) para candidato)"
                elif method == "DyV":
                    t_theory = "O(k^n) (divide la generación por mitades, no reduce la exponencialidad)"
                    s_theory = "O(n) pila recursiva"
                elif method == "ProgDin":
                    t_theory = "Depende: O(m * growth(edits)) ~ O(m * k^e)"
                    s_theory = "O(k^e) por semilla (limitada con per_seed_limit)"
                elif method == "PrimMST":
                    t_theory = "O(n^2) construcción (distancias) + O(n log n) Prim; recorrido O(n)"
                    s_theory = "O(n + e) para grafo"
                else:
                    t_theory = s_theory = "N/A"
                self.append_output(f"[THEORY] Temporal: {t_theory} | Espacial: {s_theory}")
                # si modo PRIM, dibujar MST (usar subset limitado)
                if mode == "PRIM":
                    subset, mst_edges, starts = compute_mst_for_visual(self.wordlist_entry.get(), k_neighbors=prim_k, top_n=200)
                    if subset and mst_edges:
                        self.append_output("[GUI] Abriendo ventana de visualización MST...")
                        show_mst_canvas(subset, mst_edges, starts, title="MST (Prim) visualization")
            except Exception as e:
                self.append_output(f"[ERROR] {e}")
            finally:
                self.stop_btn.config(state="disabled"); self.start_btn.config(state="normal"); self.stop_flag.clear()
        self.thread = threading.Thread(target=worker, daemon=True); self.thread.start()

# Run GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = CrackerGUI(root)
    root.mainloop()


