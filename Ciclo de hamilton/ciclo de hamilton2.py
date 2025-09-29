import itertools
import tkinter as tk
from tkinter import messagebox, filedialog
import networkx as nx
import matplotlib.pyplot as plt
import random
import openpyxl
import time

# Algoritmo de Hamilton (fuerza bruta)

def hamilton_fuerza_bruta(matriz, inicio):
    n = len(matriz)
    nodos = list(range(n))
    nodos.remove(inicio)
    ciclos = []
    
    for perm in itertools.permutations(nodos):
        camino = [inicio] + list(perm) + [inicio]
        valido = True
        costo = 0
        for i in range(len(camino)-1):
            if matriz[camino[i]][camino[i+1]] == 0:
                valido = False
                break
            else:
                costo += matriz[camino[i]][camino[i+1]]
        if valido:
            ciclos.append((camino, costo))
    return ciclos

# Funciones GUI

def generar_matriz():
    try:
        n = int(entry_nodos.get())
        if n < 2:
            raise ValueError
    except ValueError:
        messagebox.showerror("Error", "Ingrese un número válido de nodos (≥2).")
        return
    
    global matriz, n_nodos
    n_nodos = n
    matriz = [[0]*n for _ in range(n)]
    
    # Generar pesos aleatorios (1 a 10)
    for i in range(n):
        for j in range(i+1, n):
            peso = random.randint(1, 10)
            matriz[i][j] = peso
            matriz[j][i] = peso
    
    messagebox.showinfo("Éxito", "Matriz generada aleatoriamente con pesos de 1 a 10.")

def ejecutar():
    global ciclos, mejor_ciclo, mejor_costo
    
    try:
        inicio = int(entry_inicio.get())
        if inicio < 0 or inicio >= n_nodos:
            raise ValueError
    except ValueError:
        messagebox.showerror("Error", "Ingrese un nodo inicial válido.")
        return
    
    # Medir tiempo de ejecución
    inicio_tiempo = time.time()
    ciclos = hamilton_fuerza_bruta(matriz, inicio)
    fin_tiempo = time.time()
    tiempo_total = fin_tiempo - inicio_tiempo
    
    # Mostrar resultados
    text_resultados.delete("1.0", tk.END)
    
    if ciclos:
        for camino, costo in ciclos:
            text_resultados.insert(tk.END, f"Camino: {camino} | Costo: {costo}\n")
        
        # Mejor ciclo
        mejor_ciclo, mejor_costo = min(ciclos, key=lambda x: x[1])
        text_resultados.insert(tk.END, f"\n>>> Mejor ciclo: {mejor_ciclo} | Costo: {mejor_costo}\n")
        
        # Actualizar etiqueta con tiempo
        label_tiempo.config(text=f"Tiempo total de ejecución: {tiempo_total:.4f} segundos")
        
        # Dibujar grafo
        G = nx.Graph()
        for i in range(n_nodos):
            G.add_node(i)
        for i in range(n_nodos):
            for j in range(i+1, n_nodos):
                if matriz[i][j] != 0:
                    G.add_edge(i, j, weight=matriz[i][j])
        
        pos = nx.spring_layout(G)
        labels = nx.get_edge_attributes(G, 'weight')
        
        plt.figure(figsize=(6,6))
        nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=800, font_size=10)
        nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
        
        # Resaltar mejor ciclo
        edges_resaltados = [(mejor_ciclo[i], mejor_ciclo[i+1]) for i in range(len(mejor_ciclo)-1)]
        nx.draw_networkx_edges(G, pos, edgelist=edges_resaltados, edge_color='red', width=2.5)
        
        plt.title("Grafo generado - Mejor ciclo resaltado en rojo")
        plt.show()
    else:
        text_resultados.insert(tk.END, "No se encontró un ciclo de Hamilton.\n")
        label_tiempo.config(text="Tiempo total de ejecución: -")

def exportar_excel():
    if not ciclos:
        messagebox.showerror("Error", "No hay resultados para exportar. Ejecute el algoritmo primero.")
        return
    
    archivo = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
    if not archivo:
        return
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Resultados Hamilton"
    
    # Encabezados
    ws.append(["Camino", "Costo"])
    
    # Resultados
    for camino, costo in ciclos:
        ws.append([str(camino), costo])
    
    # Mejor ciclo
    ws.append([])
    ws.append(["Mejor ciclo", str(mejor_ciclo)])
    ws.append(["Costo mínimo", mejor_costo])
    
    wb.save(archivo)
    messagebox.showinfo("Éxito", f"Resultados exportados a {archivo}")

# GUI principal

root = tk.Tk()
root.title("Ciclo de Hamilton - Fuerza Bruta")

frame = tk.Frame(root)
frame.pack(pady=10)

tk.Label(frame, text="Número de nodos:").grid(row=0, column=0, padx=5, pady=5)
entry_nodos = tk.Entry(frame)
entry_nodos.grid(row=0, column=1, padx=5, pady=5)

btn_matriz = tk.Button(frame, text="Generar matriz aleatoria", command=generar_matriz)
btn_matriz.grid(row=0, column=2, padx=5, pady=5)

tk.Label(frame, text="Nodo inicial:").grid(row=1, column=0, padx=5, pady=5)
entry_inicio = tk.Entry(frame)
entry_inicio.grid(row=1, column=1, padx=5, pady=5)

btn_ejecutar = tk.Button(frame, text="Ejecutar", command=ejecutar)
btn_ejecutar.grid(row=1, column=2, padx=5, pady=5)

btn_exportar = tk.Button(frame, text="Exportar a Excel", command=exportar_excel)
btn_exportar.grid(row=2, columnspan=3, pady=10)

label_tiempo = tk.Label(root, text="Tiempo total de ejecución: -", font=("Arial", 10, "bold"))
label_tiempo.pack(pady=5)

text_resultados = tk.Text(root, width=70, height=20)
text_resultados.pack(pady=10)

# Variables globales
ciclos = []
mejor_ciclo = []
mejor_costo = 0

root.mainloop()
