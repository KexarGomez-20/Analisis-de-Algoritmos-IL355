Es importante descargar el archivo wordlist.txt para que el algoritmo se ejecute correctamente XD

Propósito del proyecto

Este proyecto tiene como objetivo mostrar, de manera educativa, cómo se puede aplicar el enfoque Divide y Vencerás (DyV) para resolver un problema de búsqueda exhaustiva o de “fuerza bruta” sobre contraseñas. El propósito principal es comparar el tiempo de ejecución de una versión paralelizada frente a una versión secuencial, y analizar cómo cambia el rendimiento cuando aumenta la longitud de la contraseña (n).

Archivos principales. cracking_gui_dyv_benchmark_embed.py (HashingFT)

Aplicación con interfaz gráfica (Tkinter) que implementa el método DyV y un modo de comparación. -Al finalizar una prueba, genera: -benchmark_results.csv: contiene los resultados del tiempo de ejecución. -benchmark_plot.png: muestra la relación entre n y el tiempo. -También se presenta la gráfica directamente dentro de la interfaz gráfica del programa. -cracking_gui_dyv_only.py — versión más simple, solo con el algoritmo DyV. -wordlist.txt — lista de palabras de ejemplo que incluye la contraseña "s3c".

Resultados del archivo CSV Cada fila del archivo benchmark_results.csv contiene los siguientes campos: method: indica el método empleado (Brute_Seq o DyV_w, donde w es el número de hilos). workers: cantidad de hilos utilizados. max_len: longitud máxima evaluada. avg_time_s: tiempo promedio de ejecución en segundos. avg_checks: cantidad promedio de combinaciones verificadas. Estos datos permiten analizar la complejidad temporal y el rendimiento de cada método.

Interpretación de los resultados. En las pruebas, es posible observar que la versión DyV puede tardar más que la versión secuencial. Esto se debe a varias razones técnicas: Sobrecarga por uso de hilos: crear y administrar hilos genera un costo adicional. Limitación del GIL: en Python, el Global Interpreter Lock impide que múltiples hilos ejecuten código intensivo de CPU al mismo tiempo. Problemas pequeños: cuando el espacio de búsqueda es reducido, la paralelización no ofrece beneficios significativos. Reparto desigual de trabajo: algunos hilos pueden recibir más combinaciones que otros. Actualización de la interfaz: las operaciones de dibujo o los mensajes de progreso también consumen tiempo adicional.

En conclusión, el enfoque DyV no modifica la complejidad teórica del problema (sigue siendo exponencial), pero permite distribuir la carga de trabajo entre varios hilos o procesos. En Python, para observar una mejora real en rendimiento, es recomendable usar multiprocessing en lugar de hilos, ya que esta técnica aprovecha todos los núcleos del procesador.
