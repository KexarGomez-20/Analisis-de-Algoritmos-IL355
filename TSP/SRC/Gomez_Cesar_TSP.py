'''
Representación del TSP

Es un grafo completo Ponderado
V: Conjunto de ciudades
E: Conjunto de aristas
w(i,j): Peso o distancias entre las ciudades i y j. Para "n" ciudades, existen (n-1)! recorridos distintos
'''

'''
TSP Simetrico: w(i,j) = w(j,i)
La distancia es la misma en ambos sentidos
------------------------------------------
TSP Asimetrico: w(i,j)≠w(j,i)
La distancia depende de la dirección
------------------------------------------
TSP Euclidiano: w(i,j)=√(xi - xj)^2 + (yi - yj)^2
Las ciudades se represntan con puntos en el plano y las distancias son ecuclidianas
'''

import numpy as np
import itertools
import tkinter as tk
from tkinter import scrolledtext #Es para el cuador de texto

#MATRIZ DE DISTANCIAS
distance_matrix = np.array([
    #Matriz cuadrada 
    #Ciudades
    #A  #B  #C  #D  #E #F #G  #H
    [0, 50, 10, 19, 8, 7, 14, 16],
    [12, 20, 9, 20, 13, 0, 18, 17],
    [6, 9, 0, 15, 16, 14, 12, 19],
    [19, 20, 15, 0, 22, 8, 17, 10],
    [8, 13, 16, 22, 0, 11, 9, 12],
    [7, 51, 14, 8, 21, 0, 10, 18],
    [14, 18, 12, 17, 9, 17, 0, 21],
    [16, 11, 19, 7, 12, 18, 21, 40]
])

#FUNCIoN PARA EVALUAR EL COSTO DE UNA RUTA
def calcular_costo(ruta, matriz):
    costo = 0
    for i in range(len(ruta) - 1):
        costo += matriz[ruta[i], ruta[i + 1]]
    costo += matriz[ruta[-1], ruta[0]]  #Regresa al inicio
    return costo

#Se agrega la distancia desde la ultima ciudad hasta la primera, despues se cierra el ciclo

#ALGORITMO DE FUERZA BRUTA
def ejecutar_tsp():
    texto.delete("1.0", tk.END)  #Limpiar pantalla

    n = distance_matrix.shape[0]
    ciudades = list(range(n))

    mejor_ruta = None
    mejor_costo = float("inf")

    texto.insert(tk.END, "Evaluación de TODAS las rutas\n\n")

    contador = 1

    for perm in itertools.permutations(ciudades): #Aqui se generan todas las permutaciones == "8! = 40320"

        #Fija la primera ciudad para evitar rutas duplicadas
        if perm[0] != 0:
            continue
        #Con esto se reduce el numero de permutas y se evitan redundancias == "(n-1)! = 5040" 

        costo = calcular_costo(perm, distance_matrix)

        texto.insert(tk.END, f"Ruta {contador}: {[c+1 for c in perm]}  |  Costo = {costo}\n") #Se suma 1 cada ciudad para que las ciudades se numeren desde 1 y no desde 0
        contador += 1

        if costo < mejor_costo:
            mejor_costo = costo
            mejor_ruta = perm

    texto.insert(tk.END, "\nRESULTADO FINAL DEL TSP\n")
    texto.insert(tk.END, f"Mejor ruta encontrada: {[c + 1 for c in mejor_ruta]}\n")
    texto.insert(tk.END, f"Distancia total mínima: {mejor_costo}\n")

#INTERFAZ GRAFICA
ventana = tk.Tk()
ventana.title("Resolución del TSP por Fuerza Bruta")
ventana.geometry("700x600")

btn_ejecutar = tk.Button(ventana, text="Ejecutar", command=ejecutar_tsp)
btn_ejecutar.pack(pady=10)

texto = scrolledtext.ScrolledText(ventana, width=80, height=30)
texto.pack()

ventana.mainloop()