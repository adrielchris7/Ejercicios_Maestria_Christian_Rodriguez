# Ejercicio 2 Descripción PEAS de agentes inteligentes

## Descripcion de PEAS

**PEAS**

- P : Performance. (Como se evalua el exito del agente?)
- E : Enviroment (En que mundo Opera, Quien mas actua ahi)
- A : Actuators (Que acciones puede ejecutar)
- S : Sensors (Que informacion puede percibir)

## Objetivo

Para cada una de las **8 aplicaciones** listadas abajo, redacta una descripción
PEAS completa y coherente. Debes pensar como diseñador del agente: qué optimiza,
dónde actúa, con qué puede mover o modificar el mundo, y qué puede observar.

## Aplicaciones a analizar

### 1. **Asistente virtual de voz**
- **Performance:**
    
    El performance de un asistente de virtual de voz se debe de medir con el porcentaje de exactitud que lectura de la peticion del usuario. De la misma manera debe de poder replicar con coherencia a lo que el usuario solicita y en un tiempo razonable, para que la experiencia de uso sea lo mas cercano a un asistente humano.

- **Enviroment:**

    Podemos decir que es el enviroment es parcialmente observable debido a que el agente solo puede detectar las peticiones pero no la intención, el estado de animo de la petición o el contexto de la pregunta.

    Tambien podemos decir que es un ambiente dinamico, ya que puede surgir una pregunta distinta durante el procesamiento.


- **Actuators:**

    Los actuadores corresponde a los equipos de sonidos conectados puede ser una bocina de auto o de un celular, en algunas ocasiones hay asistentes de voz que muestran una señal de que estan pensando o trabajando.

- **Sensors:**

    Los sensores pueden ser los microfonos que usan para detectar los comandos para interpretar la peticion del usuario. 
    Tambien pueden aplicar los sensores para iniciar el trabajo del asistente, ya sea un boton fisico, o algun sensor de proximidad para detectar que el usuario esta cerca.

### 2. **Robot aspirador domestico**

- **Performance:**
    
    El performance lo podemos medir con la superficie de limpieza que abarca el robot, tambien con la eficiencia para esquivar obstaculos, que evite caidas o atascarse mientras el usuario no se encuentra supervisando, finalmente que pueda lograr regresar adecuadamente a su base de carga.

    De igual forma podemos medir la calidad de limpieza y el uso de bateria por limpieza.

- **Enviroment:**

    El robot aspirador cuenta con un ambiente parcialmente observable, ya que su rango de visión se limita a la capacidad de la camara que tenga integrada.

    De igual forma al ser un robot automatico, no necesitamos de otro agente para su trabajo, por lo que decimos que es un agente individual.

    Tambien podemos decir que es estocástico, ya que pueden surguir escenarios nuevos, como que se caiga un vaso, o un mueble se  mueva.

- **Actuators:**

    Los actuadores son las motores para las ruedas, el motor de aspiracion, cepillos giratorios, dispensador de agua, altavoz para alertas.

- **Sensors:**

    Los sensores pueden ser los sensores de impacto, los sensores de caida, sensores infrarrojos para el mapeo, un encoder para las ruedas.

### 3. **Sistema de recomendacion de streaming**

- **Performance:**

    Para poder medir el performance de un sistema de recomendacion, podriamos decir que si la recomendacion fue buena, el usuario terminó de ver lo recomendando. 

    Por lo que se podría medir por la cantidad de minutos reproducidos, la valoración positiva o negativa sea el caso y que tan variado puede ser las sugerencias.

- **Enviroment:**

    Podemos decir que es parcialmente observable ya que se limita al registro de clicks o el tiempo de reproducción.

    Ante la elección o el rechazo, se modifica el historial y el perfil del usuario, por lo que su episodicidad es secuencial.

    Tambien es semidinamico, ya que si el usuario no tiene una interacción puede tomar las tendencial locales o globales.

- **Actuators:**

    Los actuadores son las pantalla y la interfaz de usuario

- **Sensors:**

    Los sensores pueden ser los historiales de clicks para ver el tipo de contenido visto por el usuario; el tiempo de permanencia en la recomendacion; barras de busqueda y las clasificaciones de los titulos.

### 4. **Vehiculo autonomo en ciudad**

- **Performance:**

    Para medir el performance podemos decir que lo primero en los autos autonomos es la seguiridad, que el vehiculo cumpla con las leyes de transito, limites de velocidad, y que sea cuidadoso al momento de maniobrar en la ciudad. 

    Por otro lado, como usuario, quieres que el nivel de combustible sea optimo y ahorrador, por lo que buscar que las rutas de viaje sean optimas y en un tiempo adecuado.

- **Enviroment:**

    El ambiente de un vehiculo autonomo sería que es parcialmente observable, lo cual puede ser un poco riesgoso, ante la exitencia de puntos ciegos, los sensores no pueden controlar lo que pasa en todas las partes del auto, de igual forma no puede ver lo que un auto enfrente bloquea.

    Es un ambiente multiagente ya que debe de reaccionar a los peatones, ciclistas u otros conductores.

    Tambien es dinamico ya que no siempre tendremos los mismos escenarios de tráfico.

- **Actuators:**
    
    Los actuadores son el acelerador, los frenos, las luces intermitentes, la bocina el claxon.


- **Sensors:**

    Los sensores en un auto inteligente pueden ser los sensores de deteccion de carriles, sensores de proximidad, sensores de cambio de carril, sensor de colisión.


### 5. **Agente de tradings algoritmico en bolsa**

- **Performance:**

    Puede ser la minimización del riesgo, la velocidad de ejecución de ordenes, y el retorno de inversión

- **Enviroment:**

    Es parcialmente observable ya que solo puede ver el historial de precios pero no puede ver las estrategias de otros usuarios.

    Es estocástico ya que los movimientos de los precios son impredecibles.

    Tambien es dinamicos ya que los precios cambien en segundos, por lo que siempre esta en movimiento
    

- **Actuators:**
    Envio automaticos de ordenes de compra, la venta o la cancelación a la red de la bolsa

- **Sensors:**

    Conexión de datos financieros, los indicadores economicos, noticias sobre economia, y los daotos del mercados

### 6. **Sistema de diagnosticos medicos asistido por IA**

- **Performance:**

    El performance lo podemos medir por que tan preciso es el diagnosticos, que tanta información proporciona al cliente, que tan negativos o positivos han sido los resultados.

- **Enviroment:**

    Es parcialmente observable ya que su rango es observabilidad pueden ser las imagenes medicas proporcionadas, así como los reportes medicos del paciente.

    Tambien puede ser un agente individual ya que se centra en la evaluación de un paciente a la vez.

    Es estático ya que la imagen medica o la lista de sintomas no cambia durante el analisis.

- **Actuators:**
    
    Interfa grafica de usuario, generación de reportes medicos, y las alertas de riesgo elevado.

- **Sensors:**

    Entrada de texto o de voz.  Entrada de datos sobre los sintomas o signos vitales. La carga de archivos, ya sean expedientes, radiografias o imagenes.

### 7. **Dron Inspector de infraestructura**

- **Performance:**

    En una construcción lo que el usuario busca es la seguridad, y eso lo podemos prevenir con el mantenimiento correctivo de: grietas, corrosión, y fugas. 

    Un don inspector debe de ser capaz de detectar estas 3 condiciones a tiempo, para poder prevenir accidentes mortales, por lo que tambien debemos de asegurarnos que tenga una cobertura amplia y que no queden espacios sin inspeccionar.

- **Enviroment:**

    Dentro de una estructura habrá partes en las que el dron no podrá alcanzaar, como el interior de una tubería. Por lo que es parcialmente observable.

    Tambien puede ser estocástico ya que el clima es impredecible, de igual forma la luz va cambiando dependiendo del clima y de la hora.

- **Actuators:**
    
    Al ser un dron, los actuadores son los motores de las hélices, un sistema de rotación 360 grados para la cámara y LEDs. 

- **Sensors:**

    Para la una inspección adecuada necesitamos una camara con una alta resolución, con propiedades terminas e infrarojas, un sensor LiDAR para la detección de las distancia entre los objetos, un sensor GPS, sensores de proximidad ultrasonicos.

### 8. **Agente jugador de ajedrez**

- **Performance:**

    Para un juego de ajedrez lo que buscamos son las victorias, por lo que podemos medir su efectividad por la cantidad de victorias o de derrotas, que cumpla con todas las reglas del juego, que sea no tome mucho tiempo en cada turno, y que pueda hacer su juego con la menor cantidad de movimientos.

- **Enviroment:**

    Aquí el ambiente es totalmente observable ya que el agente conoce la posición exacta de todas las piezas del tablero.

    Tambien podemos considerarlo como determinista ya que los movimientos se basan en reglas.

    Es secuencial ya que cada turno determina la estrategia para los siguientes turnos

- **Actuators:**

    En el caso de que sea un juego real, debemos de contar con un brazo robotico que pueda mover las piezas o en caso de que sea un juego online, que podamos enviar a traves de codigo los movimientos.

- **Sensors:**

    En el caso de que sea un brazo robótico, necesitamos una camara y necesitamos un sistema de sensores magneticos para poder identificar la ubicación de cada una de las piezas.