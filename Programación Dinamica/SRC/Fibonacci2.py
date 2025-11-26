import tkinter as tk
from tkinter import ttk, messagebox
import time
import matplotlib.pyplot as plt

# Algoritmos Fibonacci

def fibonacci_iterativo(n):
    """Versión sin programación dinámica (iterativa simple)."""
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b

def fibonacci_dinamico(n, memo=None):
    """Versión con programación dinámica (memoización)."""
    if memo is None:
        memo = {}
    if n in memo:
        return memo[n]
    if n <= 1:
        memo[n] = n
    else:
        memo[n] = fibonacci_dinamico(n-1, memo) + fibonacci_dinamico(n-2, memo)
    return memo[n]

def generar_secuencia_fibonacci(n, metodo):
    """Genera la secuencia Fibonacci hasta n usando el método seleccionado."""
    secuencia = []
    memo = {}
    for i in range(n + 1):
        if metodo == "Programación Dinámica":
            secuencia.append(fibonacci_dinamico(i, memo))
        else:
            secuencia.append(fibonacci_iterativo(i))
    return secuencia

# Función principal

def calcular():
    try:
        n = int(entry_numero.get())
        if n < 0:
            raise ValueError

        metodo = metodo_var.get()

        start = time.time()
        if metodo == "Programación Dinámica":
            resultado = fibonacci_dinamico(n, {})
        else:
            resultado = fibonacci_iterativo(n)
        end = time.time()

        tiempo = (end - start) * 1000  # ms

        # Generar secuencia
        secuencia = generar_secuencia_fibonacci(n, metodo)

        etiqueta_resultado.config(
            text=f"F({n}) = {resultado}\n"
                 f"Tiempo: {tiempo:.4f} ms\n"
                 f"Secuencia: {secuencia}"
        )

    except ValueError:
        messagebox.showerror("Error", "Ingresa un número entero no negativo.")

# Limpiar resultado

def limpiar_resultado():
    entry_numero.delete(0, tk.END)
    etiqueta_resultado.config(text="")

# Comparar tiempos


def graficar_comparacion():
    valores = list(range(5, 31))  # rango pequeño por eficiencia
    tiempos_iterativo = []
    tiempos_dinamico = []

    for n in valores:
        # Sin programación dinámica (iterativo)
        start = time.time()
        fibonacci_iterativo(n)
        tiempos_iterativo.append((time.time() - start) * 1000)

        # Con programación dinámica
        start = time.time()
        fibonacci_dinamico(n, {})
        tiempos_dinamico.append((time.time() - start) * 1000)

    plt.figure(figsize=(9, 5))
    plt.plot(valores, tiempos_iterativo, label="Sin Programación Dinámica", marker='o')
    plt.plot(valores, tiempos_dinamico, label="Programación Dinámica", marker='s')
    plt.title("Comparación de tiempos: Fibonacci", fontsize=14)
    plt.xlabel("n", fontsize=12)
    plt.ylabel("Tiempo (ms)", fontsize=12)
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()

# Interfaz gráfica (Tkinter)

ventana = tk.Tk()
ventana.title("Comparación Fibonacci: Dinámico vs Sin Dinámica")
ventana.geometry("600x400")

titulo = tk.Label(ventana, text="Serie de Fibonacci", font=("Arial", 16, "bold"))
titulo.pack(pady=10)

frame = tk.Frame(ventana)
frame.pack(pady=10)

# Entrada de número
tk.Label(frame, text="Ingresa el número n:").grid(row=0, column=0, padx=5, pady=5)
entry_numero = tk.Entry(frame, width=10)
entry_numero.grid(row=0, column=1, padx=5, pady=5)

# Select bar (Combobox) para método
tk.Label(frame, text="Selecciona el método:").grid(row=1, column=0, padx=5, pady=5)
metodo_var = tk.StringVar()
metodo_combo = ttk.Combobox(frame, textvariable=metodo_var, state="readonly",
                            values=["Programación Dinámica", "Sin Programación Dinámica"])
metodo_combo.grid(row=1, column=1, padx=5, pady=5)
metodo_combo.current(0)

# Botones
boton_calcular = ttk.Button(ventana, text="Calcular Fibonacci", command=calcular)
boton_calcular.pack(pady=5)

boton_limpiar = ttk.Button(ventana, text="Limpiar Resultado", command=limpiar_resultado)
boton_limpiar.pack(pady=5)

boton_graficar = ttk.Button(ventana, text="Mostrar Gráfica Comparativa", command=graficar_comparacion)
boton_graficar.pack(pady=5)

# Resultado
etiqueta_resultado = tk.Label(ventana, text="", font=("Arial", 12), wraplength=550, justify="left")
etiqueta_resultado.pack(pady=15)

ventana.mainloop()