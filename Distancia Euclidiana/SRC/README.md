Par Más Cercano (Distancia Euclidiana)
Aplicación gráfica desarrollada en Python + Tkinter que permite ingresar un conjunto de puntos en el plano y calcular el par de puntos más cercanos utilizando la distancia euclidiana.
Incluye llenado aleatorio de coordenadas, validación de datos y presentación de resultados mediante ventanas emergentes.

Características principales: 
- Cálculo del par más cercano entre 5 puntos.
- Uso de la distancia euclidiana para medir la proximidad.
- Interfaz gráfica sencilla desarrollada con Tkinter.
- Botón para rellenar automáticamente coordenadas al azar.
- Botón para limpiar los campos.
- Gestión de errores mediante messagebox.

Funcionamiento de la aplicación
Entrada de puntos

El usuario debe ingresar 5 puntos, cada uno con coordenadas (x, y).
La aplicación muestra una tabla de entradas:

P1   x  y
P2   x  y
P3   x  y
P4   x  y
P5   x  y

Botones disponibles
Botón	Función
Calcular ----------- Determina los dos puntos más cercanos y muestra la distancia.
Llenar Random------- Llena las coordenadas con valores aleatorios entre 0 y 40.
Limpiar ------------ Limpia todas las entradas.

Cálculo del par más cercano
El algoritmo evalúa todas las posibles combinaciones de pares utilizando fuerza bruta:
'''
for i in range(n):
    for j in range(i+1, n):
'''
Para cada par aplica la distancia euclidiana:
'''
np.linalg.norm(p1 - p2)
'''

Complejidad del algoritmo
El método utilizado es fuerza bruta, por lo que su complejidad es:
O(n²)

Suficiente para conjuntos pequeños (como los 5 puntos usados aquí).
