Comparación de Algoritmos de Búsqueda (Lineal vs Binaria)

Aplicación desarrollada en Python + Tkinter que permite comparar el rendimiento temporal entre los algoritmos de búsqueda lineal y búsqueda binaria sobre listas de diferentes tamaños.
Incluye generación de datos, ejecución de búsquedas, visualización de tiempos en gráficas y exportación de datos.

Características principales
- Implementación de dos algoritmos de búsqueda:
    - Búsqueda lineal
    - Búsqueda binaria
- Interface gráfica desarrollada con Tkinter
- Generación automática de datos aleatorios ordenados
- Medición de tiempos en milisegundos
- Gráfica comparativa con Matplotlib (escala logarítmica en eje X)
- Exportación de datos generados a archivos CSV/TXT
- Función de reinicio completo (datos + gráfica)

Estructura del programa

El código se divide en tres secciones principales:
1. Algoritmos de búsqueda
  - Lineal
Recorre la lista elemento por elemento.
  - Binaria
Funciona únicamente sobre listas ordenadas, usando división del intervalo de búsqueda.

'''
def busqueda_lineal(lista, valor): ...
def busqueda_binaria(lista, valor): ...
'''

2. Clase "BusquedaApp"
Administra toda la interfaz y lógica de interacción:

° Generación de listas
° Lectura del valor a buscar
° Ejecución de algoritmos
° Medición de tiempo
° Graficación de resultados
° Exportación de archivos

3. Ejecución de la ventana principal
'''
if __name__ == "__main__":
    root = tk.Tk()
    app = BusquedaApp(root)
    root.mainloop()
'''
Funcionamiento de la interfaz
Generación de datos
El usuario selecciona el tamaño de lista:
"100, 1000, 10000, 100000"
Luego pulsa “Generar datos” y la aplicación crea números aleatorios (0–999), ordenados.

Búsquedas
Se escribe un valor y se elige:
° Búsqueda lineal
° Búsqueda binaria
Cada ejecución guarda:
° Tamaño de la lista
° Tiempo medido

Gráfica de resultados
Al presionar “Actualizar gráfica”:
° Se dibuja una curva para búsquedas lineales
° Otra para búsquedas binarias
° Se usa escala logarítmica en el eje X para ver mejor las diferencias de complejidad

Exportación
Los datos generados se exportan en formato:
 ->  .csv
 ->  .txt

Mediante la opción “Exportar números”

Reinicio
La opción “Reiniciar” borra:
- Lista generada
- Resultados medidos
- Texto del resultado
- Gráfica

Complejidad algorítmica
Algoritmo	Complejidad (peor caso)
Lineal	O(n)
Binaria	O(log n)

La gráfica generada permite observar estas diferencias claramente conforme aumenta el tamaño de los datos.
