Resolución del Problema del Viajante (TSP) mediante Fuerza Bruta con Interfaz Gráfica

Este proyecto implementa una solución al Problema del Viajante (Traveling Salesman Problem, TSP) utilizando un enfoque de fuerza bruta,
evaluando todas las permutaciones posibles de rutas para encontrar la de menor costo.
El sistema incluye una interfaz gráfica en Tkinter que muestra en tiempo real cada ruta evaluada junto con su costo total.

Características
- Permite evaluar todas las rutas posibles para un conjunto de ciudades definidas en una matriz de distancias.
- Utiliza el algoritmo de fuerza bruta al generar todas las permutaciones del conjunto de ciudades.
- Para evitar rutas redundantes, se fija la primera ciudad, reduciendo el número total de permutaciones de n! a (n-1)!.
- Muestra en pantalla:
  ° Cada ruta generada
  ° El costo total de recorrerla
  ° La mejor ruta encontrada
  ° El costo mínimo obtenido
- Incluye una interfaz gráfica construida con Tkinter, usando un botón para ejecutar el algoritmo y un cuadro de texto desplazable para mostrar los resultados.

Tipos de TSP considerados
Aunque el código implementa un TSP ponderado genérico, se documentan los tipos de TSP:
- TSP Simétrico: w(i,j) = w(j,i) La distancia es igual en ambas direcciones.
- TSP Asimétrico: w(i,j) ≠ w(j,i) La distancia depende de la dirección.

TSP Euclidiano: w(i,j) = √((xi - xj)² + (yi - yj)²) Las ciudades representan puntos en el plano con distancia euclidiana.

Estructura del Código
1. Matriz de Distancias
El programa utiliza una matriz cuadrada numpy que representa las distancias entre ciudades. El índice de cada ciudad inicia en 0.

2. Cálculo del costo de una ruta
La función calcular_costo(ruta, matriz) recorre la ruta sumando las distancias de cada tramo y cerrando el ciclo al volver a la ciudad inicial.

3. Algoritmo de Fuerza Bruta
Se generan todas las permutaciones posibles con itertools.permutations.
Para evitar rutas duplicadas, se fija la primera ciudad, generando únicamente (n-1)! rutas.

4. Interfaz Gráfica en Tkinter
Incluye:
- Ventana principal
- Botón para ejecutar el algoritmo
- Cuadro de texto desplazable para mostrar los resultados

Ejecución
Para ejecutar el programa, asegúrate de tener instalado Python y las bibliotecas:
numpy
tkinter (incluido en la instalación estándar de Python)
No se requiere instalación adicional.
