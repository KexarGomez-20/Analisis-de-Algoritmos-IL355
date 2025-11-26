Comparación de Métodos para Calcular la Serie de Fibonacci
Aplicación gráfica con Tkinter

Este proyecto implementa y compara dos métodos para calcular la serie de Fibonacci:

- Método iterativo tradicional (sin programación dinámica)
- Método con programación dinámica (memoización)

Incluye una interfaz gráfica desarrollada con Tkinter, así como una gráfica comparativa de tiempos usando Matplotlib.

Características principales
- Cálculo de Fibonacci(n) mediante:
  ° Algoritmo iterativo simple.
  ° Algoritmo con memoización (programación dinámica).
- Visualización de:
  ° Valor de F(n)
  ° Tiempo de ejecución (milisegundos)
  ° Secuencia completa desde 0 hasta n
- Gráfica comparativa del rendimiento entre ambos métodos.
- Interfaz intuitiva desarrollada con Tkinter.

Ejecución

Aparecerá una ventana con:
- Entrada para el valor de n
- Menú desplegable para elegir el método
- Botones para:
  ° Calcular Fibonacci
  ° Limpiar resultados
  ° Mostrar la gráfica comparativa

Descripción técnica del código
1. Métodos de cálculo de Fibonacci

fibonacci_iterativo(n)
Implementación clásica, recorre de 2 a n acumulando los valores.

fibonacci_dinamico(n, memo)
Utiliza memoización para evitar recalcular valores previamente obtenidos.

generar_secuencia_fibonacci(n, metodo)
Devuelve la secuencia completa desde F(0) hasta F(n).

2. Cálculo y visualización

La función calcular():
- Obtiene el valor ingresado.
- Determina el método seleccionado.
- Calcula F(n) y mide el tiempo de ejecución.
- Muestra:
  ° Resultado
  ° Tiempo en ms
  ° Secuencia generada

3. Gráfica comparativa

La función graficar_comparacion():
- Evalúa ambos métodos para valores de n entre 5 y 30.
- Registra los tiempos en milisegundos.
- Genera una gráfica usando Matplotlib que compara ambos enfoques.

Interfaz Gráfica (Tkinter)

La aplicación incluye:
- Entry para capturar n
- Combobox para seleccionar el método
- Botones:
  ° Calcular Fibonacci
  ° Limpiar resultado
  ° Mostrar gráfica comparativa
- Etiqueta para los resultados
- Ventana principal de tamaño 600×400
