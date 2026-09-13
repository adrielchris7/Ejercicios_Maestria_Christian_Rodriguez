## Reporte de Análisis de Algoritmos de Búsqueda no Informada

En el presente reporte se analiza el comportamiento de los algoritmos de búsqueda no informada en el mapa de las ciudades de Rumania, tomando como origen la ciudad de **Zerind** y como destino **Eforie**.

### Breadth-First Search (BFS) y Uniform-Cost Search (UCS)

* **BFS:** El resultado de la aplicación del algoritmo BFS es que encuentra el camino con menos carreteras (menor número de aristas o pasos), ignorando el costo físico (kilómetros) para llegar a la meta. El algoritmo exploró nivel por nivel y, al estar la meta a una distancia de 7 conexiones, encontró la solución en la profundidad $d = 7$ siguiendo la ruta:
  *Zerind → Arad → Sibiu → Fagaras → Bucharest → Urziceni → Hirsova → Eforie*

* **UCS:** Por el contrario, este algoritmo priorizó el costo acumulado $g(n)$ de cada ruta para tomar la de menor valor en kilómetros hasta la meta. Aunque el algoritmo tomó más conexiones intermedias, la distancia real en kilómetros de la ruta ganadora fue menor que en BFS:
  *Zerind → Arad → Sibiu → Rimnicu Vilcea → Pitesti → Bucharest → Urziceni → Hirsova → Eforie*

### Depth-First Search (DFS)

En este algoritmo no se logró encontrar la ruta con éxito debido a que cayó en un bucle infinito (ciclos entre ciudades) al no controlar estados repetidos. 

Dada su estrategia de exploración a ciegas ("profundizar primero"), DFS avanza a lo largo de una rama sin evaluar los costos ni comparar alternativas. Su resultado depende totalmente del orden en que se exploren las ciudades vecinas en la estructura de datos (por ejemplo, elegir `Arad` u `Oradea` primero), lo que puede llevar al algoritmo a dar un rodeo masivo por todo el mapa o a quedarse atrapado en un ciclo sin llegar a la meta.

### Depth-Limited Search (DLS) y su relación con BFS / IDS

Para las ciudades seleccionadas no fue suficiente el parámetro `--limit 3`, ya que al estar la meta a mayor profundidad, DLS devolvió un estado de `cutoff`. Fue necesario aumentar el parámetro a **`--limit 7`** para obtener una respuesta exitosa.

El límite en 7 tiene una relación directa con la cantidad de saltos que BFS utilizó para llegar al destino ($d = 7$). Cualquier límite menor a 7 corta la búsqueda prematuramente y devuelve `cutoff`. En el caso de **IDS**, el algoritmo ejecuta DLS de forma iterativa (`limit = 0, 1, 2...`), devolviendo `cutoff` en las primeras iteraciones hasta alcanzar exactamente el nivel 7, donde logra encontrar a Eforie con éxito y con el mínimo uso de memoria.