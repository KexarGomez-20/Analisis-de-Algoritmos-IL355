import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import numpy as np
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ---------------------------
# Algoritmos de búsqueda
# ---------------------------
def busqueda_lineal(lista, valor):
    for i, v in enumerate(lista):
        if v == valor:
            return i
    return -1

def busqueda_binaria(lista, valor):
    izquierda, derecha = 0, len(lista) - 1
    while izquierda <= derecha:
        medio = (izquierda + derecha) // 2
        if lista[medio] == valor:
            return medio
        elif lista[medio] < valor:
            izquierda = medio + 1
        else:
            derecha = medio - 1
    return -1

# ---------------------------
# Clase principal de la app
# ---------------------------
class BusquedaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Comparación de Búsqueda Lineal y Binaria")
        self.lista = []

        # Parámetros
        self.tamanos = [100, 1000, 10000, 100000]

        # --- Acumuladores de resultados para graficar ---
        self.resultados_lineal = []   # lista de tuplas (n, tiempo_ms)
        self.resultados_binaria = []  # lista de tuplas (n, tiempo_ms)

        # Widgets
        self.crear_widgets()

        # Figura para la gráfica
        self.fig, self.ax = plt.subplots(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def crear_widgets(self):
        frame_config = tk.Frame(self.root)
        frame_config.pack(pady=10)

        # Selector de tamaño
        tk.Label(frame_config, text="Tamaño de lista:").grid(row=0, column=0, padx=5)
        self.combo_size = ttk.Combobox(frame_config, values=self.tamanos, state="readonly", width=12)
        self.combo_size.set(self.tamanos[0])
        self.combo_size.grid(row=0, column=1, padx=5)

        # Botón generar datos
        tk.Button(frame_config, text="Generar datos", command=self.generar_datos).grid(row=0, column=2, padx=5)

        # Entrada de valor a buscar
        tk.Label(frame_config, text="Valor a buscar:").grid(row=1, column=0, padx=5)
        self.entry_valor = tk.Entry(frame_config, width=14)
        self.entry_valor.grid(row=1, column=1, padx=5)

        # Botones de búsqueda
        tk.Button(frame_config, text="Búsqueda lineal", command=self.ejecutar_lineal).grid(row=1, column=2, padx=5)
        tk.Button(frame_config, text="Búsqueda binaria", command=self.ejecutar_binaria).grid(row=1, column=3, padx=5)

        # Botones extra: Reiniciar y Exportar
        tk.Button(frame_config, text="Reiniciar", command=self.reiniciar).grid(row=2, column=2, padx=5, pady=5)
        tk.Button(frame_config, text="Exportar números", command=self.exportar_numeros).grid(row=2, column=3, padx=5, pady=5)

        # Resultados
        self.label_resultado = tk.Label(self.root, text="Resultado: ")
        self.label_resultado.pack(pady=10)

        # Botón actualizar gráfica
        tk.Button(self.root, text="Actualizar gráfica", command=self.actualizar_grafica).pack(pady=5)

    def generar_datos(self):
        tam = int(self.combo_size.get())
        # Genera números y ordena (necesario para binaria)
        self.lista = sorted(np.random.randint(0, 1000, tam))
        # Se modificó el tamaño del randint en tu código original por ser demasiados números
        #self.lista = sorted(np.random.randint(0, 1000, tam))
        self.label_resultado.config(text=f"Lista generada con tamaño {tam}")

    def ejecutar_lineal(self):
        if not self.lista:
            messagebox.showwarning("Error", "Primero genera la lista.")
            return
        try:
            valor = int(self.entry_valor.get())
        except ValueError:
            messagebox.showwarning("Error", "Introduce un valor válido.")
            return

        inicio = time.perf_counter()
        indice = busqueda_lineal(self.lista, valor)
        fin = time.perf_counter()
        ms = (fin - inicio) * 1000

        # Guardar punto para la gráfica
        self.resultados_lineal.append((len(self.lista), ms))

        if indice != -1:
            self.label_resultado.config(
                text=f"[Lineal] Tamaño: {len(self.lista)}, Valor {valor} encontrado en índice {indice}, Tiempo: {ms:.4f} ms"
            )
        else:
            self.label_resultado.config(
                text=f"[Lineal] Tamaño: {len(self.lista)}, Valor {valor} no encontrado, Tiempo: {ms:.4f} ms"
            )

    def ejecutar_binaria(self):
        if not self.lista:
            messagebox.showwarning("Error", "Primero genera la lista.")
            return
        try:
            valor = int(self.entry_valor.get())
        except ValueError:
            messagebox.showwarning("Error", "Introduce un valor válido.")
            return

        inicio = time.perf_counter()
        indice = busqueda_binaria(self.lista, valor)
        fin = time.perf_counter()
        ms = (fin - inicio) * 1000

        # Guardar punto para la gráfica
        self.resultados_binaria.append((len(self.lista), ms))

        if indice != -1:
            self.label_resultado.config(
                text=f"[Binaria] Tamaño: {len(self.lista)}, Valor {valor} encontrado en índice {indice}, Tiempo: {ms:.4f} ms"
            )
        else:
            self.label_resultado.config(
                text=f"[Binaria] Tamaño: {len(self.lista)}, Valor {valor} no encontrado, Tiempo: {ms:.4f} ms"
            )

    def actualizar_grafica(self):
        self.ax.clear()

        if self.resultados_lineal:
            xs_l, ys_l = zip(*self.resultados_lineal)
            self.ax.plot(xs_l, ys_l, 'o-', label="Búsqueda Lineal")
        if self.resultados_binaria:
            xs_b, ys_b = zip(*self.resultados_binaria)
            self.ax.plot(xs_b, ys_b, 'o-', label="Búsqueda Binaria")

        self.ax.set_title("Comparación de tiempos (ms) vs tamaño")
        self.ax.set_xlabel("Tamaño de la lista (n)")
        self.ax.set_ylabel("Tiempo (ms)")

        # ---- cambio clave: semilogaritmica ----
        self.ax.set_xscale("log")

        self.ax.legend()
        self.ax.grid(True, which="both", ls=":")

        self.canvas.draw()

    def reiniciar(self):
        """Limpia lista, resultados y gráfica."""
        self.lista = []
        self.resultados_lineal.clear()
        self.resultados_binaria.clear()
        self.entry_valor.delete(0, tk.END)
        self.label_resultado.config(text="Resultado: ")
        # Limpia la gráfica
        self.ax.clear()
        self.ax.set_title("Comparación de tiempos (ms) vs tamaño")
        self.ax.set_xlabel("Tamaño de la lista (n)")
        self.ax.set_ylabel("Tiempo (ms)")
        self.ax.grid(True)
        self.canvas.draw()
        messagebox.showinfo("Reiniciar", "Se limpió la lista y los resultados.")

    def exportar_numeros(self):
        """Exporta los números generados a un CSV (uno por línea)."""
        if not self.lista:
            messagebox.showwarning("Exportar", "No hay números que exportar. Genera la lista primero.")
            return

        ruta = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv"), ("Texto", "*.txt"), ("Todos", "*.*")],
            initialfile=f"numeros_{len(self.lista)}.csv",
            title="Guardar números generados"
        )
        if not ruta:
            return  # usuario canceló

        try:
            # Guardar uno por línea (columna única)
            np.savetxt(ruta, np.array(self.lista, dtype=int), fmt="%d", delimiter=",")
            messagebox.showinfo("Exportar", f"Números exportados a:\n{ruta}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar el archivo:\n{e}")

# ---------------------------
# Ejecutar la app
# ---------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = BusquedaApp(root)
    root.mainloop()
