import tkinter as tk
from tkinter import messagebox
import numpy as np
import random


# Función de distancia Euclidiana

def distancia_euclidiana(p1, p2):
    p1, p2 = np.array(p1), np.array(p2)
    return np.linalg.norm(p1 - p2)


# Función para encontrar par más cercano

def par_mas_cercano(puntos):
    min_dist = float("inf")
    par = None
    n = len(puntos)
    for i in range(n):
        for j in range(i+1, n):
            dist = distancia_euclidiana(puntos[i], puntos[j])
            if dist < min_dist:
                min_dist = dist
                par = (puntos[i], puntos[j])
    return par, min_dist

# Funciones GUI

def calcular():
    try:
        puntos = []
        for i in range(5):
            x = int(entries[i][0].get())
            y = int(entries[i][1].get())
            puntos.append((x, y))
        
        par, dist = par_mas_cercano(puntos)
        messagebox.showinfo("Resultado", 
                            f"Los puntos más cercanos son {par[0]} y {par[1]}\n"
                            f"Distancia: {dist:.2f}")
    except ValueError:
        messagebox.showerror("Error", "Por favor ingresa números válidos.")

def llenar_random():
    for i in range(5):
        x = random.randint(0, 40)
        y = random.randint(0, 40)
        entries[i][0].delete(0, tk.END)
        entries[i][0].insert(0, str(x))
        entries[i][1].delete(0, tk.END)
        entries[i][1].insert(0, str(y))

def limpiar():
    for i in range(5):
        entries[i][0].delete(0, tk.END)
        entries[i][1].delete(0, tk.END)

# Interfaz gráfica

root = tk.Tk()
root.title("Par más cercano")

# Entradas
entries = []
for i in range(5):
    tk.Label(root, text=f"P{i+1}").grid(row=i, column=0, padx=5, pady=5)
    e1 = tk.Entry(root, width=5)
    e2 = tk.Entry(root, width=5)
    e1.grid(row=i, column=1, padx=5, pady=5)
    e2.grid(row=i, column=2, padx=5, pady=5)
    entries.append((e1, e2))

# Botones
tk.Button(root, text="Calcular", command=calcular).grid(row=6, column=0, pady=10)
tk.Button(root, text="Llenar Random", command=llenar_random).grid(row=6, column=1, pady=10)
tk.Button(root, text="Limpiar", command=limpiar).grid(row=6, column=2, pady=10)

root.mainloop()