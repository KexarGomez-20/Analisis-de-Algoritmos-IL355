import tkinter as tk
from tkinter import ttk, messagebox
import random

# ----------------------
# Algoritmos (generadores)
# ----------------------
def selection_sort(data):
    n = len(data)
    for i in range(n - 1):
        min_idx = i
        yield data, get_color_array(len(data), comparing=(i, min_idx))
        for j in range(i + 1, n):
            yield data, get_color_array(len(data), comparing=(j, min_idx))
            if data[j] < data[min_idx]:
                min_idx = j
                yield data, get_color_array(len(data), comparing=(i, min_idx))
        if min_idx != i:
            data[i], data[min_idx] = data[min_idx], data[i]
            yield data, get_color_array(len(data), swapping=(i, min_idx))
        yield data, get_color_array(len(data), sorted_index=i)
    yield data, get_color_array(len(data), final=True)

def bubble_sort(data):
    n = len(data)
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            yield data, get_color_array(len(data), comparing=(j, j + 1))
            if data[j] > data[j + 1]:
                data[j], data[j + 1] = data[j + 1], data[j]
                swapped = True
                yield data, get_color_array(len(data), swapping=(j, j + 1))
        yield data, get_color_array(len(data), sorted_index=n - i - 1)
        if not swapped:
            break
    yield data, get_color_array(len(data), final=True)

def merge_sort(data):
    def merge_sort_gen(arr, left, right):
        if left >= right: return
        mid = (left + right) // 2
        yield from merge_sort_gen(arr, left, mid)
        yield from merge_sort_gen(arr, mid + 1, right)
        temp = []
        i, j = left, mid + 1
        while i <= mid and j <= right:
            yield arr, get_color_array(len(arr), comparing=(i, j))
            if arr[i] <= arr[j]:
                temp.append(arr[i]); i += 1
            else:
                temp.append(arr[j]); j += 1
        while i <= mid: temp.append(arr[i]); i += 1
        while j <= right: temp.append(arr[j]); j += 1
        for k, val in enumerate(temp):
            arr[left + k] = val
            yield arr, get_color_array(len(arr), merging=(left + k,))
    if len(data) <= 1:
        yield data, get_color_array(len(data), final=True); return
    yield from merge_sort_gen(data, 0, len(data) - 1)
    yield data, get_color_array(len(data), final=True)

def quick_sort(data):
    def quick_gen(arr, low, high):
        if low < high:
            pivot = arr[high]; i = low - 1
            yield arr, get_color_array(len(arr), pivot_index=high)
            for j in range(low, high):
                yield arr, get_color_array(len(arr), comparing=(j, high))
                if arr[j] < pivot:
                    i += 1; arr[i], arr[j] = arr[j], arr[i]
                    yield arr, get_color_array(len(arr), swapping=(i, j))
            arr[i + 1], arr[high] = arr[high], arr[i + 1]
            pivot_index = i + 1
            yield arr, get_color_array(len(arr), swapping=(pivot_index, high))
            yield from quick_gen(arr, low, pivot_index - 1)
            yield from quick_gen(arr, pivot_index + 1, high)
        elif low == high:
            yield arr, get_color_array(len(arr), sorted_index=low)
    if len(data) <= 1:
        yield data, get_color_array(len(data), final=True); return
    yield from quick_gen(data, 0, len(data) - 1)
    yield data, get_color_array(len(data), final=True)

# ----------------------
# Colores
# ----------------------
def get_color_array(n, comparing=None, swapping=None, merging=None, sorted_index=None, pivot_index=None, final=False):
    default, comparing_col, swapping_col = "#6fa8dc", "#ffd966", "#e06666"
    merging_col, sorted_col, pivot_col = "#b4a7d6", "#93c47d", "#f6b26b"
    colors = [default] * n
    if final: return [sorted_col] * n
    if comparing: 
        for idx in comparing: colors[idx] = comparing_col
    if swapping: 
        for idx in swapping: colors[idx] = swapping_col
    if merging: 
        for idx in merging: colors[idx] = merging_col
    if sorted_index is not None:
        if isinstance(sorted_index, int): sorted_index = (sorted_index,)
        for idx in sorted_index: colors[idx] = sorted_col
    if pivot_index is not None: colors[pivot_index] = pivot_col
    return colors

# ----------------------
# GUI
# ----------------------
class VisualizadorOrdenamiento:
    def __init__(self, root):
        self.root, self.data = root, []
        root.title("Visualizador de Métodos de Ordenamiento")
        root.resizable(False, False)

        self.algorithms = {
            "Selection Sort": selection_sort,
            "Bubble Sort": bubble_sort,
            "Merge Sort": merge_sort,
            "Quick Sort": quick_sort
        }

        self.selected_alg = tk.StringVar(value="Selection Sort")
        self.speed = tk.IntVar(value=50)
        self.n_barras_var = tk.StringVar(value="50")
        self.generator, self.is_sorting = None, False

        control_frame = ttk.Frame(root, padding=8)
        control_frame.grid(row=0, column=0, sticky="ew")

        ttk.Label(control_frame, text="Algoritmo:").grid(row=0, column=0, padx=4)
        ttk.OptionMenu(control_frame, self.selected_alg, self.selected_alg.get(), *self.algorithms.keys()).grid(row=0, column=1, padx=4)

        ttk.Label(control_frame, text="N barras:").grid(row=0, column=2, padx=4)
        self.entry_n = ttk.Entry(control_frame, textvariable=self.n_barras_var, width=6)
        self.entry_n.grid(row=0, column=3, padx=4)

        ttk.Button(control_frame, text="Generar", command=self.generate_data).grid(row=0, column=4, padx=4)
        ttk.Button(control_frame, text="Mezclar", command=self.shuffle_data).grid(row=0, column=5, padx=4)
        ttk.Button(control_frame, text="Ordenar", command=self.start_sort).grid(row=0, column=6, padx=4)
        ttk.Button(control_frame, text="Limpiar", command=self.clear_highlights).grid(row=0, column=7, padx=4)

        ttk.Label(control_frame, text="Velocidad (ms):").grid(row=1, column=0, padx=4, pady=6)
        self.scale_speed = ttk.Scale(control_frame, from_=0, to=200, variable=self.speed, orient=tk.HORIZONTAL, command=self.update_speed_label)
        self.scale_speed.grid(row=1, column=1, columnspan=2, sticky="ew", padx=4)
        self.lbl_speed_val = ttk.Label(control_frame, text=f"{self.speed.get()} ms")
        self.lbl_speed_val.grid(row=1, column=3, padx=4)

        # Botón pausa (stop)
        self.btn_pause = ttk.Button(control_frame, text="Pausar", command=self.stop_sort, state="disabled")
        self.btn_pause.grid(row=1, column=4, padx=4)

        self.canvas_width, self.canvas_height = 900, 400
        self.canvas = tk.Canvas(root, width=self.canvas_width, height=self.canvas_height, bg="white")
        self.canvas.grid(row=1, column=0, padx=8, pady=8)

        self.generate_data()

    def update_speed_label(self, event=None):
        self.lbl_speed_val.config(text=f"{self.speed.get()} ms")

    def generate_data(self):
        try: n = int(self.n_barras_var.get())
        except ValueError: n = 50; self.n_barras_var.set("50")
        self.data = [random.randint(5, 390) for _ in range(n)]
        self.draw_data(self.data, ["#6fa8dc"] * len(self.data))

    def shuffle_data(self):
        if not self.data: return
        random.shuffle(self.data)
        self.draw_data(self.data, ["#6fa8dc"] * len(self.data))

    def clear_highlights(self):
        if not self.data: return
        self.draw_data(self.data, ["#6fa8dc"] * len(self.data))

    def draw_data(self, data, color_array):
        self.canvas.delete("all")
        c_w, c_h = self.canvas_width, self.canvas_height
        n = len(data) if data else 1
        bar_width, max_val = max(c_w / n, 1), max(data) if data else 1
        for i in range(6):
            val = int(max_val * (i / 5))
            y = c_h - (val / max_val) * (c_h - 20)
            self.canvas.create_line(0, y, c_w, y, fill="#ddd")
            self.canvas.create_text(5, y, anchor="sw", text=str(val), fill="black", font=("Arial", 8))
        for i, val in enumerate(data):
            x0, x1 = i * bar_width, (i + 1) * bar_width
            bar_height = (val / max_val) * (c_h - 20)
            y0, y1 = c_h - bar_height, c_h
            color = color_array[i] if i < len(color_array) else "#6fa8dc"
            self.canvas.create_rectangle(x0 + 1, y0, x1 - 1, y1, fill=color, outline="")
            if n <= 30:
                self.canvas.create_text((x0 + x1) / 2, y0 - 10, text=str(val), font=("Arial", 8), fill="black")
        self.canvas.create_text(10, 10, anchor="nw", text=f"N={n}, Algoritmo={self.selected_alg.get()}")

    def start_sort(self):
        if self.is_sorting or not self.data:
            if not self.data: messagebox.showwarning("Sin datos", "Genera primero la lista.")
            return
        alg_func = self.algorithms.get(self.selected_alg.get())
        self.generator = alg_func(self.data)
        self.is_sorting = True
        self.btn_pause.config(state="normal")
        self.disable_controls()
        self.run_generator_step()

    def run_generator_step(self):
        if not self.generator: return
        try:
            data, color_array = next(self.generator)
            self.draw_data(data, color_array)
            self.root.after(self.speed.get(), self.run_generator_step)
        except StopIteration:
            self.draw_data(self.data, get_color_array(len(self.data), final=True))
            self.is_sorting, self.generator = False, None
            self.enable_controls()
            self.btn_pause.config(state="disabled")

    def stop_sort(self):
        """Detener ordenamiento y reactivar botones"""
        self.is_sorting, self.generator = False, None
        self.enable_controls()
        self.btn_pause.config(state="disabled")

    def disable_controls(self):
        for child in self.root.winfo_children():
            if isinstance(child, ttk.Frame):
                for w in child.winfo_children():
                    w.configure(state="disabled")
        self.btn_pause.configure(state="normal")

    def enable_controls(self):
        for child in self.root.winfo_children():
            if isinstance(child, ttk.Frame):
                for w in child.winfo_children():
                    w.configure(state="normal")
        self.btn_pause.configure(state="disabled")

def main():
    root = tk.Tk()
    app = VisualizadorOrdenamiento(root)
    root.mainloop()

if __name__ == "__main__":
    main()
