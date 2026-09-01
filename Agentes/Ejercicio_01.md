# Ejercicio 1

## Agentes Inteligentes

### Diseño original del mapa del wumpus

```yaml
grid:
  width: 4
  height: 4

agent:
  start: [1, 1]
  direction: east
  arrows: 1

wumpus: [1, 3]

pits:
  - [3, 1]
  - [3, 3]
  - [4, 4]

gold: [2, 3]
```
### Esta es la estrucura original del mapa.

```yaml

Step 0  Score 0  IN CAVE
 4 | .  .  .  P 
 3 | W  G  P  . 
 2 | .  .  .  . 
 1 | >  .  P  . 
      1  2  3  4
Percept [None]

Legend: >^v< agent  P pit  W wumpus  w dead wumpus  G gold  . empty  ## wall
```