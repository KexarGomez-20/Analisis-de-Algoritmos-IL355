Ciclo de Hamilton por Fuerza Bruta
Aplicación gráfica con Python + Tkinter que genera un grafo aleatorio y encuentra todos los ciclos Hamiltonianos usando fuerza bruta, mostrando además el ciclo de costo mínimo y permitiendo exportar los resultados a Excel.
Incluye visualización gráfica del grafo con NetworkX y resaltado del mejor ciclo.

Características principales
- Generación de una matriz de adyacencia con pesos aleatorios entre 1 y 10.
- Ejecución del algoritmo de ciclo Hamiltoniano por fuerza bruta.
- Cálculo de:
  ° Todos los ciclos válidos encontrados.
  ° Mejor ciclo (menor costo).
  °Tiempo total de ejecución.
- Visualización del grafo con NetworkX:
  ° Nodos y aristas etiquetadas.
  ° Mejor ciclo resaltado en color rojo.
- Exportación de resultados a Excel (.xlsx).
- Interfaz gráfica intuitiva desarrollada con Tkinter.

Funcionamiento de la aplicación
1. Generación de matriz aleatoria
El usuario ingresa un número de nodos n ≥ 2, y el sistema genera automáticamente una matriz de adyacencia simétrica con pesos aleatorios entre 1 y 10.
Ejemplo:
  0   1   2   3
0 -   4   8   2
1 4   -   5   7
2 8   5   -   6
3 2   7   6   -

2. Selección de nodo inicial
Se ingresa el nodo desde el cual se desea iniciar la búsqueda del ciclo Hamiltoniano.

3. Ejecución del algoritmo
El botón "Ejecutar":
- Calcula todos los ciclos Hamiltonianos posibles.
- Mide el tiempo de ejecución.
- Muestra los ciclos y sus costos.
- Identifica el mejor ciclo (costo mínimo).
- Dibuja el grafo y resalta el mejor ciclo.

4. Exportación a Excel
La opción "Exportar a Excel" genera un archivo .xlsx con:
- Todos los ciclos encontrados y sus costos.
- Mejor ciclo.
- osto mínimo.

Algoritmo Utilizado
Se usa fuerza bruta generando todas las permutaciones posibles:
'''
for perm in itertools.permutations(nodos):
    camino = [inicio] + list(perm) + [inicio]
'''
Para cada ciclo:
- Se revisa si el camino es válido.
- Se suma el costo total.
- Se almacena el resultado.

Complejidad
O((n-1)!)

Muy costoso para grafos grandes; adecuado solo para propósitos académicos y experimentales.

Visualización del grafo
La aplicación usa NetworkX y Matplotlib:

- Nodos representados visualmente.
- Aristas etiquetadas con su peso.
- El mejor ciclo se resalta en color rojo.

Ejemplo:

(0)──4──(1)
 │      │
 2      7
 │      │
(3)──6──(2)
