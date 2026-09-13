## Reporte de Análisis de Greedy Best First vs A*

### Desempeño de ambos algoritmos

* Durante la prueba para la ruta Zerind --> Craiova, el algoritmo A* encontró la ruta más optima con menor kilometraje (441 km):

```Texto
Zerind → Arad → Sibiu → Rimnicu Vilcea → Craiova
```

Posteriormente, el algoritmo `Greedy` coincidió con A* y tuvo la misma ruta. Esto se debe a que la distancia euclidiana hacia Craiova decrece de manera continua a lo largo del trayecto. Como resultado en cada paso hacia la siguiente ciudad coincidió con el camino de menor costo.

### ¿Por qué Greedy puede devolver un camino más caro, aunque `h` sea admisible?

Podemos decir que la heurística es admisible cuando la distancia estimada (h) nunca sobrepasa el costo real que falta para llegar a la meta. 

Greedy puede dar una ruta costosa a pesar de tener una heurística admisible debido a que la toma de decisiones la hace de manera ciega, e ignora el costo real ya recorrido por carretera. Solo se guía por la ciudad que parece estar más cerca, sin importar si tomar rutas por carreteras más largar o hacer zig zags entre ciudades

Por el contrario, A* evalúa **f(n) = g(n) + h(n)** verificando el pasado y el futuro, lo que le permite evitar vueltas innecesarias y garantiza la ruta más corta.

### En el camino de A*, ¿`f` tiende a **no disminuir** a lo largo de la ruta? Relaciónalo con que `h` sea consistente 

En la ruta explorada por A*, los valores de la función mostraron una tendencia no decreciente [283 --> 335 --> 390 --> 419 --> 441].

Esto se debe a que la heurística usada es consistente. Eso garantiza que para cualquier ciudad conectada, la estimación de la línea recta desde la primera ciudad nunca supera el costo real del tramo más la estimación desde la segunda ciudad.

Al momento de verificar los valores generados calculados por coordenadas, podemos verificar que satisfacen la desigualdad triangular de la geometría. Lo que significa que la f(n) nunca disminuye a lo largo de la ruta. 
