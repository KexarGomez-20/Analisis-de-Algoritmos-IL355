import tkinter as tk
import random
import time
import matplotlib.pyplot as plt

 #Generador de listas aleatorias

def Generador(N):
    """Genera una lista de N números enteros aleatorios."""
    return [random.randint(50, 10000) for _ in range(N)]

# Algoritmos de ordenamiento

def bubble_sort(arr):
    arr = arr.copy()
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr


def merge_sort(arr):
    arr = arr.copy()
    if len(arr) > 1:
        mid = len(arr) // 2
        L = merge_sort(arr[:mid])
        R = merge_sort(arr[mid:])

        merged = []
        i = j = 0
        while i < len(L) and j < len(R):
            if L[i] < R[j]:
                merged.append(L[i])
                i += 1
            else:
                merged.append(R[j])
                j += 1
        merged.extend(L[i:])
        merged.extend(R[j:])
        return merged
    else:
        return arr


def quick_sort(arr):
    arr = arr.copy()
    if len(arr) <= 1:
        return arr
    else:
        pivot = arr[0]
        menores = [x for x in arr[1:] if x <= pivot]
        mayores = [x for x in arr[1:] if x > pivot]
        return quick_sort(menores) + [pivot] + quick_sort(mayores)

# Ordenador

def Ordenador(lista, algoritmo):
    """Ordena la lista usando el algoritmo seleccionado."""
    inicio = time.perf_counter()

    if algoritmo == "Bubble":
        Ordenada = bubble_sort(lista)
    elif algoritmo == "Merge":
        Ordenada = merge_sort(lista)
    elif algoritmo == "Quick":
        Ordenada = quick_sort(lista)
    else:
        raise ValueError("Algoritmo no soportado")

    fin = time.perf_counter()
    return fin - inicio, Ordenada


# Graficador

def Graficador():
    tamaños = list(range(50,1050,50)) # [50, 100, 200, 400, 600, 800, 1000]
    algoritmos = ["Bubble", "Merge", "Quick"]
    resultados = {alg: [] for alg in algoritmos}

    for n in tamaños:
        lista = Generador(n)
        print(f"\n🔹 Tamaño de lista: {n}")
        for alg in algoritmos:
            tiempo, _ = Ordenador(lista, alg)
            resultados[alg].append(tiempo)
            print(f"{alg}: {tiempo:.6f} seg")

    # Tabla de resultados
    print("\n=== TABLA COMPARATIVA ===")
    print("N\tBubble\t\tMerge\t\tQuick")
    for i, n in enumerate(tamaños):
        print(f"{n}\t{resultados['Bubble'][i]:.6f}\t{resultados['Merge'][i]:.6f}\t{resultados['Quick'][i]:.6f}")

    # Gráfica
    plt.figure(figsize=(10, 6))
    for alg in algoritmos:
        plt.plot(tamaños, resultados[alg], marker="o", label=alg)

    plt.xlabel("Tamaño de la lista (N)")
    plt.ylabel("Tiempo de ejecución (segundos)")
    plt.title("Comparación de Algoritmos de Ordenamiento")
    plt.legend()
    plt.grid(True)
    plt.show()



# Ejecución principal

if __name__ == "__main__":
    Graficador()