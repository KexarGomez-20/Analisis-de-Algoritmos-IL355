import tkinter as tk
from tkinter import ttk, messagebox
import time
import matplotlib.pyplot as plt

# ------------------------------
# Algoritmos Fibonacci
# ------------------------------

def fibonacci_divide_y_venceras(n):
    """Versión recursiva pura (divide y vencerás)."""
    if n <= 1:
        return n
    return fibonacci_divide_y_venceras(n-1) + fibonacci_divide_y_venceras(n-2)

def fibonacci_dinamico(n, memo={}):
    """Versión con programación dinámica (memoización)."""
    if n in memo:
        return memo[n]
    if n <= 1:
        memo[n] = n
    else:
        memo[n] = fibonacci_dinamico(n-1, memo) + fibonacci_dinamico(n-2, memo)
    return memo[n]

# ------------------------------
# Función principal
# ------------------------------

def calcular():
    try:
        n = int(entry_numero.get())
        if n < 0:
            raise ValueError

        usar_dinamico = bool(scale_var.get())

        start = time.time()
        if usar_dinamico:
            resultado = fibonacci_dinamico(n, {})
        else:
            resultado = fibonacci_divide_y_venceras(n)
        end = time.time()

        tiempo = (end - start) * 1000  # milisegundos
        etiqueta_resultado.config(
            text=f"F({n}) = {resultado}\nTiempo: {tiempo:.4f} ms"
        )

    except ValueError:
        messagebox.showerror("Error", "Ingresa un número entero no negativo.")

# ------------------------------
# Comparar tiempos
# ------------------------------

def graficar_comparacion():
    valores = list(range(5, 31))  # rangos pequeños por eficiencia
    tiempos_dividir = []
    tiempos_dinamico = []

    for n in valores:
        # Divide y vencerás
        start = time.time()
        fibonacci_divide_y_venceras(n)
        tiempos_dividir.append((time.time() - start) * 1000)

        # Dinámico
        start = time.time()
        fibonacci_dinamico(n, {})
        tiempos_dinamico.append((time.time() - start) * 1000)

    plt.figure(figsize=(8, 5))
    plt.plot(valores, tiempos_dividir, label="Divide y Vencerás", marker='o')
    plt.plot(valores, tiempos_dinamico, label="Programación Dinámica", marker='s')
    plt.title("Comparación de tiempos: Fibonacci")
    plt.xlabel("n")
    plt.ylabel("Tiempo (ms)")
    plt.legend()
    plt.grid(True)
    plt.show()

# ------------------------------
# Interfaz gráfica (Tkinter)
# ------------------------------

ventana = tk.Tk()
ventana.title("Comparación Fibonacci: Divide y Vencerás vs Programación Dinámica")
ventana.geometry("500x350")

titulo = tk.Label(ventana, text="Serie de Fibonacci", font=("Arial", 16, "bold"))
titulo.pack(pady=10)

frame = tk.Frame(ventana)
frame.pack(pady=10)

tk.Label(frame, text="Ingresa el número n:").grid(row=0, column=0, padx=5, pady=5)
entry_numero = tk.Entry(frame, width=10)
entry_numero.grid(row=0, column=1, padx=5, pady=5)

scale_var = tk.IntVar(value=1)
tk.Label(frame, text="Usar programación dinámica:").grid(row=1, column=0, padx=5, pady=5)
tk.Scale(frame, from_=0, to=1, orient="horizontal", variable=scale_var,
         length=150, tickinterval=1).grid(row=1, column=1, padx=5, pady=5)

boton_calcular = ttk.Button(ventana, text="Calcular Fibonacci", command=calcular)
boton_calcular.pack(pady=10)

etiqueta_resultado = tk.Label(ventana, text="", font=("Arial", 12))
etiqueta_resultado.pack(pady=10)

boton_graficar = ttk.Button(ventana, text="Mostrar Gráfica Comparativa", command=graficar_comparacion)
boton_graficar.pack(pady=10)

ventana.mainloop()
