## Ejercicio 1 Comparar BFS, UCS, DFS, DLS E IDS en el mapa de Rumania


### Objetivo 
 Elegir una ruta distinta de Arad --> Bucharest, correr BFS, UCS, DFS, DLS e IDS, y analizar diferencias de camino, costo, profundidad y nodos expandidos.


### Pareja que se va a usar
**Zerind --> Eforie**

## Tabla comparativa de los resultados de los algoritmos para la pareja de ciudades.

A continuacion se presentan los algoritmos de busqueda usados y los resultados de las rutas:

| Algoritmo | Status | Depth | Cost | Expanded | Generated | Path |
|:---|:---:|:---:|:---:|:---:|:---:|:---|
| **Breadth First Search (BFS)** | `Success` | 7 Roads | 794 km | 16 Nodes | 40 Nodes | Zerind → Arad → Sibiu → Fagaras → Bucharest → Urziceni → Hirsova → Eforie |
| **Uniform Cost Search (UCS)** | `Success` | 8 Roads | 762 km | 17 Nodes | 43 Nodes | Zerind → Arad → Sibiu → Rimnicu Vilcea → Bucharest → Urziceni → Hirsova → Eforie |
| **Depth First Search (DFS)** | `Cutoff` | N/A | N/A | 6 Nodes | 18 Nodes | N/A |
| **DFS (limit 2)** | `Cutoff` | N/A | N/A | 3 Nodes | 8 Nodes | N/A |
| **DFS (limit 4)** | `Cutoff` | N/A | N/A | 13 Nodes | 35 Nodes | N/A |
| **Iterative Deepening Search (IDS)** | `Success` | 7 Roads | 794 km | 92 Nodes | 248 Nodes | Zerind → Arad → Sibiu → Fagaras → Bucharest → Urziceni → Hirsova → Eforie |


## Diagramas ASCII de las rutas encontradas por los algoritmos.

*Diagrama de Ruta - BFS & IDS (Costo: 794 km)*

[Zerind] 75 km → [Arad] 140 km → [Sibiu] 99 km → [Fagaras] 211 km → [Bucharest] 85 km → [Urziceni] 98 km → [Hirsova] 86 km →[Eforie]


*Diagrama de Ruta - Uniform Cost Search (Costo Óptimo: 762 km)*

[Zerind] 75 km → [Arad] 140 km → [Sibiu] 80 km → [Rimnicu Vilcea] 97 km → [Pitesti] 101 km → [Bucharest] 85 km → [Urziceni] 98 km → [Hirsova] 86 km → [Eforie]

## Conclusión 

