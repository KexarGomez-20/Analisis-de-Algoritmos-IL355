Comparación de Algoritmos de Ordenamiento en Python
Este proyecto implementa y compara tres algoritmos clásicos de ordenamiento: Bubble Sort, Merge Sort y Quick Sort.
El programa genera listas aleatorias de diferentes tamaños, mide el tiempo de ejecución de cada algoritmo y muestra una gráfica comparativa del rendimiento.

Contenido
- Generador de listas aleatorias.
- Implementación de los algoritmos de ordenamiento:
  ° Bubble Sort
  ° Merge Sort
  ° Quick Sort
- Función de medición de tiempo para cada algoritmo.
- Generación de tabla comparativa.
- Gráfica de rendimiento utilizando Matplotlib.

Ejecución
El programa:
1. Generará listas con tamaños desde 50 hasta 1000 elementos.
2. Ordenará cada lista con los tres algoritmos.
3. Mostrará los tiempos de ejecución en consola.
4. Abrirá una gráfica comparativa del rendimiento.

Descripción de las funciones principales
Generador(N)
Genera una lista de N números enteros aleatorios entre 50 y 10000.

Algoritmos de ordenamiento
- bubble_sort
Implementación clásica del método burbuja.
- merge_sort
Divide recursivamente la lista en mitades y las combina ordenadas.
- quick_sort
Selecciona un pivote y divide la lista en listas menores y mayores para ordenarlas recursivamente.

Ordenador(lista, algoritmo)
Ejecuta el algoritmo seleccionado y mide el tiempo de ejecución usando time.perf_counter.

Graficador()
Evalúa los algoritmos para tamaños crecientes de listas. Muestra:

- Tiempos de ejecución por consola.
- Tabla comparativa.
- Gráfica de rendimiento con Matplotlib.

Salida gráfica
La gráfica compara:
- Eje X: tamaño de la lista.
- Eje Y: tiempo de ejecución en segundos.
- Tres curvas: Bubble, Merge y Quick.
