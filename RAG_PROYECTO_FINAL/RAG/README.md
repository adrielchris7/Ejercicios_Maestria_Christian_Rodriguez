# Sistema RAG — Backend (FastAPI) + UI (Streamlit)

Sistema de Retrieval-Augmented Generation que permite subir documentos (PDF, TXT, MD),
indexarlos en una base vectorial (ChromaDB) usando embeddings de Google AI, y hacer
preguntas sobre su contenido. El modelo responde únicamente con base en la evidencia
recuperada y se abstiene explícitamente cuando no la hay.

## Estructura del proyecto

```
RAG/
├── app/
│   ├── main.py       # Endpoints de FastAPI
│   ├── chunk.py       # Extracción de texto y fragmentación en chunks
│   ├── embed.py        # Cliente de embeddings de Google AI
│   ├── generate.py       # Cliente de generación (Gemini) + construcción del prompt
│   └── store.py       # Wrapper de ChromaDB (persistencia, búsqueda, borrado)
├── ui/
│   └── streamlit_app.py # Interfaz de chat
├── chroma/           # Base vectorial persistente (NO se sube a git)
├── .env               # Variables de entorno reales (NO se sube a git)
├── .env.example       # Plantilla de variables de entorno
├── .gitignore
├── requirements.txt
└── README.md
```

## 1. Requisitos previos

- Python 3.11+ instalado.
- Una API key de Google AI Studio: https://aistudio.google.com/app/apikey

## 2. Crear y activar el entorno virtual

Desde la raíz del proyecto (`RAG/`):

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

> Si PowerShell bloquea la ejecución de scripts, corre una vez:
> `Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned`

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

## 3. Instalar dependencias

Con el venv activado:

```bash
pip install -r requirements.txt
```

## 4. Configurar la clave de la API

Copia la plantilla y pega tu clave real:

```bash
cp .env.example .env        # macOS/Linux
copy .env.example .env      # Windows
```

Edita `.env` y completa:

```
GOOGLE_API_KEY=tu_clave_aqui
```

El archivo `.env` está en `.gitignore` — nunca se sube al repositorio.

Opcionalmente puedes ajustar el umbral de abstención (ver sección 7):

```
ABSTENTION_DISTANCE_THRESHOLD=0.8
```

## 5. Levantar el backend (API)

En una terminal, con el venv activado:

```bash
uvicorn app.main:app --reload --port 8000
```

Verifica que esté viva en: http://127.0.0.1:8000/health
Deberías ver algo como:

```json
{
  "status": "ok",
  "message": "Backend RAG operativo",
  "chroma": "ok",
  "chroma_chunks_indexados": 0,
  "embeddings_disponibles": true,
  "generacion_disponible": true
}
```

Si `embeddings_disponibles` o `generacion_disponible` salen en `false`, revisa que
`GOOGLE_API_KEY` esté bien configurada en tu `.env`.

## 6. Levantar la interfaz (UI)

En **otra terminal** (deja la de uvicorn corriendo), con el venv activado:

```bash
streamlit run ui/streamlit_app.py
```

Se abre automáticamente en: http://localhost:8501

## 7. Probar el sistema end-to-end

1. En la UI, ve a la pestaña **Configuración** → sube un PDF, TXT o MD de prueba y
   dale **"Procesar e Ingestar Documento(s)"**.
2. Ve a la pestaña **Chat** y escribe una pregunta sobre el contenido de ese documento.
3. Deberías ver la respuesta generada, junto con un expander **"Referencias"** que
   muestra los fragmentos usados (fuente, página y distancia/score).
4. Prueba también con una pregunta totalmente fuera de tema (ej. "¿cuál es la capital
   de Mongolia?" si tu documento no tiene nada que ver) — el sistema debe **abstenerse**
   en vez de inventar una respuesta.

También puedes probar la API directamente, sin la UI:

```bash
curl -X POST http://127.0.0.1:8000/query \
  -H "Content-Type: application/json" \
  -d "{\"question\": \"¿De qué trata el documento?\", \"top_k\": 3}"
```

## 8. Regla de abstención

El sistema usa **dos capas** de abstención, para no depender únicamente del criterio del modelo generador:

### Capa 1 — Umbral de distancia (antes de llamar al modelo generador)

Cada chunk recuperado de ChromaDB trae un `score`, que es la **distancia coseno**
entre el embedding de la pregunta y el embedding del chunk (la colección se crea
explícitamente con `hnsw:space="cosine"` en `store.py`). Este valor va de:

- `0.0` → el chunk es prácticamente idéntico semánticamente a la pregunta.
- `1.0` → no hay relación (vectores ortogonales).
- `2.0` → sentido opuesto.

Si **no se recuperó ningún chunk**, o el chunk más parecido tiene una distancia
mayor al umbral configurado, el sistema se abstiene de inmediato y **ni siquiera
llama a Gemini** (ahorra cuota y evita alucinaciones):

```python
ABSTENTION_DISTANCE_THRESHOLD = float(os.getenv("ABSTENTION_DISTANCE_THRESHOLD", "0.8"))

if not retrieved_chunks or retrieved_chunks[0]["score"] > ABSTENTION_DISTANCE_THRESHOLD:
    # abstención
```

El valor por defecto es `0.8` y es **configurable** vía la variable de entorno
`ABSTENTION_DISTANCE_THRESHOLD` en `.env`. Es un punto de partida, no un valor
definitivo: debe calibrarse empíricamente con el corpus real del proyecto —
subiendo el valor si el sistema se abstiene demasiado seguido ante preguntas
válidas, o bajándolo si deja pasar preguntas que debería rechazar.

### Capa 2 — Instrucción explícita al modelo generador

Incluso si los chunks recuperados pasan el umbral de distancia, puede que no
contengan realmente la respuesta a la pregunta (son "parecidos" pero no
"suficientes"). Por eso el prompt enviado a Gemini (`generate.py`) incluye una
instrucción explícita:

> Si el contexto no contiene información suficiente para responder la pregunta,
> responde EXACTAMENTE: "No tengo evidencia suficiente en los documentos para
> responder esa pregunta."

La respuesta del modelo se compara contra ese mensaje exacto para marcar
`abstained: true` en la respuesta de la API.

### Por qué dos capas

- La **Capa 1** es rápida, barata (no gasta cuota de generación) y protege contra
  corpus vacíos o preguntas totalmente fuera de dominio.
- La **Capa 2** cubre el caso más sutil donde los chunks recuperados pasan el
  umbral de similitud pero, al leerlos, no responden realmente la pregunta —
  algo que un umbral numérico por sí solo no puede detectar.

## 9. Endpoints de la API

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/health` | Estado de la API, de Chroma y de los servicios de Google AI |
| POST | `/ingest` | Sube e indexa uno o varios documentos (`files`) y/o rutas del servidor (`paths`) |
| POST | `/query` | Hace una pregunta (`question`, `top_k` opcional) |
| GET | `/documents` | Lista los documentos indexados y su cantidad de chunks |
| DELETE | `/documents/{filename}` | Elimina un documento específico |
| DELETE | `/documents` | Reinicia toda la colección (borra todo el índice) |

## 10. Problemas comunes

- **`429 RESOURCE_EXHAUSTED` al ingestar**: se agotó la cuota gratuita de la API de
  Gemini (límite de solicitudes por minuto o por día). `embed.py` ya reintenta
  automáticamente con backoff exponencial ante este error; si persiste, espera
  unos minutos o revisa tu plan en https://ai.dev/rate-limit.
- **`404 NOT_FOUND` con un modelo (`text-embedding-004`, `gemini-2.5-flash`, etc.)**:
  Google retira modelos periódicamente. Revisa el mensaje de error (suele indicar
  el modelo de reemplazo) y actualiza el `model_name` en `embed.py` o `generate.py`.
- **No puedes borrar la carpeta `chroma/` manualmente**: detén primero `uvicorn`
  (Windows bloquea el archivo `chroma.sqlite3` mientras el proceso sigue vivo), o
  usa el endpoint `DELETE /documents` / el botón "Reiniciar base vectorial" en la
  pestaña de Configuración de la UI.