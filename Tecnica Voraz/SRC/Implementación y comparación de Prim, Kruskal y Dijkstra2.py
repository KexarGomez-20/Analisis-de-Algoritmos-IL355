import tkinter as tk
from tkinter import ttk, messagebox
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time
import heapq

# -------- Grafo (nodos A..G fijos) --------
G = nx.Graph()
edges = [
    ('A','C',3),
    ('A','D',4),
    ('A','E',4),
    ('C','B',2),
    ('C','E',4),
    ('C','G',5),
    ('B','F',2),
    ('F','G',5),
    ('E','D',2),
    ('E','G',5)
]
G.add_weighted_edges_from(edges)

pos = nx.spring_layout(G, seed=42)

# -------- TK / GUI --------
root = tk.Tk()
root.title("EquipoX - Prim, Kruskal & Dijkstra (Visualizador)")
root.geometry("920x560")

# Matplotlib figure inside Tk
fig, ax = plt.subplots(figsize=(6,5))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas_widget = canvas.get_tk_widget()
canvas_widget.grid(row=0, column=0, rowspan=12, padx=8, pady=8)

# Right panel (controls + output)
control_frame = ttk.Frame(root)
control_frame.grid(row=0, column=1, sticky="n", padx=(4,12))

txt = tk.Text(root, height=25, width=48)
txt.grid(row=1, column=1, padx=(4,12), pady=(8,8), sticky="n")

# Utils: draw graph with optional highlights and visited nodes
def draw_graph(highlight_edges=None, visited_nodes=None, edge_color='green'):
    ax.clear()
    # node colors: visited -> lightgreen, else lightblue
    node_colors = []
    for n in G.nodes():
        if visited_nodes and n in visited_nodes:
            node_colors.append('lightgreen')
        else:
            node_colors.append('lightblue')

    nx.draw(G, pos, ax=ax, with_labels=True, node_color=node_colors, node_size=700)
    labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)

    if highlight_edges:
        # normalize edges to undirected shape
        norm_edges = []
        for u,v in highlight_edges:
            if (u,v) in G.edges():
                norm_edges.append((u,v))
            elif (v,u) in G.edges():
                norm_edges.append((v,u))
        nx.draw_networkx_edges(G, pos, edgelist=norm_edges, width=3, edge_color=edge_color)

    canvas.draw()
    root.update()

# initial draw
draw_graph()

# ---- Controls: node selectors ----
nodes_sorted = sorted(list(G.nodes()))
ttk.Label(control_frame, text="Start node (Prim):").grid(row=0, column=0, sticky="w", pady=(4,0))
prim_start_var = tk.StringVar(value=nodes_sorted[0])
cb_prim = ttk.Combobox(control_frame, textvariable=prim_start_var, values=nodes_sorted, state="readonly", width=10)
cb_prim.grid(row=1, column=0, pady=(0,8))

ttk.Label(control_frame, text="Start node (Dijkstra):").grid(row=2, column=0, sticky="w", pady=(4,0))
dij_start_var = tk.StringVar(value='D' if 'D' in nodes_sorted else nodes_sorted[0])
cb_dij_start = ttk.Combobox(control_frame, textvariable=dij_start_var, values=nodes_sorted, state="readonly", width=10)
cb_dij_start.grid(row=3, column=0, pady=(0,8))

ttk.Label(control_frame, text="Target node (Dijkstra):").grid(row=4, column=0, sticky="w", pady=(4,0))
dij_target_var = tk.StringVar(value=nodes_sorted[-1])
cb_dij_target = ttk.Combobox(control_frame, textvariable=dij_target_var, values=nodes_sorted, state="readonly", width=10)
cb_dij_target.grid(row=5, column=0, pady=(0,8))

# Sleep speeds
SLEEP = 0.45

# ---- PRIM (with heap) ----
def run_prim():
    txt.delete("1.0", tk.END)
    start = prim_start_var.get()
    if start not in G.nodes():
        messagebox.showerror("Error", "Nodo inicial inválido para Prim.")
        return

    visited = set([start])
    pq = []
    mst = []
    for v, data in G[start].items():
        heapq.heappush(pq, (data['weight'], start, v))

    highlighted = []
    t0 = time.perf_counter()
    # initially show start visited
    draw_graph(highlighted, visited_nodes=visited)
    root.update()
    time.sleep(SLEEP)

    while pq and len(visited) < len(G.nodes()):
        w, u, v = heapq.heappop(pq)
        if v in visited:
            continue
        visited.add(v)
        mst.append((u, v, w))
        highlighted.append((u, v))
        draw_graph(highlighted, visited_nodes=visited, edge_color='green')
        root.update()
        time.sleep(SLEEP)
        for nxt, data in G[v].items():
            if nxt not in visited:
                heapq.heappush(pq, (data['weight'], v, nxt))
    t1 = time.perf_counter()

    total = sum(w for _,_,w in mst)
    txt.insert(tk.END, "=== PRIM ===\n")
    txt.insert(tk.END, f"Start: {start}\n\n")
    for u,v,w in mst:
        txt.insert(tk.END, f"{u} - {v} : {w}\n")
    txt.insert(tk.END, f"\nPeso total: {total}\n")
    txt.insert(tk.END, f"Tiempo: {t1-t0:.6f} s\n")
    txt.insert(tk.END, "\nComplejidad (aprox): O(E log V)\n")

# ---- KRUSKAL (Union-Find) ----
class UnionFind:
    def __init__(self, elements):
        self.parent = {e:e for e in elements}
        self.rank = {e:0 for e in elements}
    def find(self,x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]
    def union(self,a,b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.rank[ra] < self.rank[rb]:
            self.parent[ra] = rb
        else:
            self.parent[rb] = ra
            if self.rank[ra] == self.rank[rb]:
                self.rank[ra] += 1
        return True

def run_kruskal():
    txt.delete("1.0", tk.END)
    uf = UnionFind(G.nodes())
    sorted_edges = sorted(G.edges(data=True), key=lambda x: x[2]['weight'])
    mst = []
    highlighted = []
    t0 = time.perf_counter()
    for u,v,data in sorted_edges:
        if uf.union(u,v):
            w = data['weight']
            mst.append((u,v,w))
            highlighted.append((u,v))
            draw_graph(highlighted, edge_color='green')
            root.update()
            time.sleep(SLEEP)
        if len(mst) == len(G.nodes()) - 1:
            break
    t1 = time.perf_counter()
    total = sum(w for _,_,w in mst)
    txt.insert(tk.END, "=== KRUSKAL ===\n\n")
    for u,v,w in mst:
        txt.insert(tk.END, f"{u} - {v} : {w}\n")
    txt.insert(tk.END, f"\nPeso total: {total}\n")
    txt.insert(tk.END, f"Tiempo: {t1-t0:.6f} s\n")
    txt.insert(tk.END, "\nComplejidad (aprox): O(E log E) ≈ O(E log V)\n")

# ---- DIJKSTRA (with origin & target) ----
def run_dijkstra():
    txt.delete("1.0", tk.END)
    source = dij_start_var.get()
    target = dij_target_var.get()
    if source not in G.nodes() or target not in G.nodes():
        messagebox.showerror("Error", "Nodos inválidos para Dijkstra.")
        return

    dist = {n: float('inf') for n in G.nodes()}
    prev = {n: None for n in G.nodes()}
    dist[source] = 0
    pq = [(0, source)]
    highlighted = []
    t0 = time.perf_counter()

    visited_in_loop = set()
    while pq:
        d,u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        # mark the edge from prev[u] -> u as explored (if any)
        if prev[u]:
            highlighted.append((prev[u], u))
        draw_graph(highlighted, visited_nodes=visited_in_loop, edge_color='purple')
        root.update()
        time.sleep(0.15)

        if u == target:
            break

        visited_in_loop.add(u)
        for v, attrs in G[u].items():
            w = attrs['weight']
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                prev[v] = u
                heapq.heappush(pq, (nd, v))

    t1 = time.perf_counter()

    if dist[target] == float('inf'):
        txt.insert(tk.END, "No existe camino entre esos nodos.\n")
        txt.insert(tk.END, f"Tiempo: {t1-t0:.6f} s\n")
        return

    # reconstruct final path
    final_path = []
    cur = target
    while prev[cur] is not None:
        final_path.insert(0, (prev[cur], cur))
        cur = prev[cur]

    draw_graph(final_path, edge_color='orange')
    root.update()

    txt.insert(tk.END, "=== DIJKSTRA ===\n")
    txt.insert(tk.END, f"Origen: {source}\nDestino: {target}\n\n")
    for n in sorted(dist.keys()):
        val = "∞" if dist[n] == float('inf') else str(dist[n])
        txt.insert(tk.END, f"{source} -> {n} = {val}\n")
    txt.insert(tk.END, f"\nDistancia al destino: {dist[target]}\n")
    txt.insert(tk.END, f"Tiempo: {t1-t0:.6f} s\n")
    txt.insert(tk.END, "\nComplejidad (aprox): O(E log V)\n")

# ---- Buttons (created separately then placed) ----
btn_prim = ttk.Button(control_frame, text="Ejecutar Prim", command=run_prim, width=22)
btn_prim.grid(row=6, column=0, pady=(8,4))

btn_kruskal = ttk.Button(control_frame, text="Ejecutar Kruskal", command=run_kruskal, width=22)
btn_kruskal.grid(row=7, column=0, pady=4)

btn_dijkstra = ttk.Button(control_frame, text="Ejecutar Dijkstra", command=run_dijkstra, width=22)
btn_dijkstra.grid(row=8, column=0, pady=4)

btn_reset = ttk.Button(control_frame, text="Reiniciar visual", command=lambda: draw_graph(), width=22)
btn_reset.grid(row=9, column=0, pady=(10,4))

info = (
    "Instrucciones:\n"
    "- Selecciona el nodo de inicio para Prim o Dijkstra.\n"
    "- Selecciona el nodo destino para Dijkstra (opcional).\n"
    "- Presiona el botón del algoritmo deseado.\n\n"
    "Salida:\n"
    "- PRIM/KRUSKAL: aristas seleccionadas y peso total + tiempo.\n"
    "- DIJKSTRA: tabla de distancias desde el origen + tiempo.\n"
)
lbl_info = ttk.Label(control_frame, text=info, wraplength=220, justify="left")
lbl_info.grid(row=10, column=0, pady=(6,2))

root.mainloop()
