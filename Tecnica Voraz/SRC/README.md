Visualizador de Algoritmos de Grafos
Prim • Kruskal • Dijkstra
Interfaz gráfica con Tkinter + NetworkX + Matplotlib

Este proyecto implementa un visualizador interactivo de tres algoritmos fundamentales en teoría de grafos:
- Árbol de Expansión Mínima (MST)
  ° Prim
  ° Kruskal
- Camino más corto
  ° Dijkstra

Incluye una interfaz gráfica (GUI) con Tkinter, renderizado de grafos con NetworkX y animaciones mediante Matplotlib.

Características principales
- Grafo predefinido con nodos A..G y ponderaciones.
- Visualización gráfica del grafo:
  ° Aristas resaltadas durante la ejecución.
  ° Nodos visitados resaltados.
- Ejecución paso a paso con pausas animadas.
- Panel informativo con:
  ° Aristas elegidas por Prim/Kruskal
  ° Camino más corto de Dijkstra
  ° Pesos finales
  ° Tiempos de ejecución
  ° Complejidad computacional
- Selector de nodos de inicio y destino para Dijkstra.
- Botón para reiniciar la visualización.

Descripción del Grafo
El grafo contiene nodos:
A, B, C, D, E, F, G

Aristas ponderadas:
| Nodo 1 | Nodo 2 | Peso |
| ------ | ------ | ---- |
| A      | C      | 3    |
| A      | D      | 4    |
| A      | E      | 4    |
| C      | B      | 2    |
| C      | E      | 4    |
| C      | G      | 5    |
| B      | F      | 2    |
| F      | G      | 5    |
| E      | D      | 2    |
| E      | G      | 5    |

Interfaz Gráfica
Panel izquierdo
Muestra el grafo actualizado de forma gráfica:
- Aristas resaltadas (verde o morado/ naranja según algoritmo).
- Nodos visitados (verde claro).
- Camino final (naranja en Dijkstra).

Panel derecho
Contiene:
- Selectores de nodos (start/target)
- Botones:
  ° Ejecutar Prim
  ° Ejecutar Kruskal
  ° Ejecutar Dijkstra
  ° Reiniciar visual
- Cuadro de texto con resultados detallados
- Instrucciones

Descripción de los algoritmos
1. Prim
- Usa una cola de prioridad (heapq).
- Construye un árbol de expansión mínima.
- Resalta aristas conforme son seleccionadas.
-Complejidad aproximada:
    O(E log V)

2. Kruskal
- Ordena aristas por peso.
- Utiliza estructura Union-Find con compresión de caminos.
- Selecciona aristas sin formar ciclos.
- Complejidad aproximada:
    O(E log E)

3. Dijkstra
- Calcula distancias mínimas desde nodo origen.
- Anima la exploración de nodos y aristas.
- Reconstruye el camino más corto al nodo destino.
- Complejidad aproximada:
    O(E log V)
