import os
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from app.chunk import extract_text_from_file, create_chunks
from app.embed import GoogleEmbeddingClient
from app.store import VectorStore
from app.generate import GeminiGenerator, ABSTENTION_MESSAGE

app = FastAPI(title="RAG API Backend", version="1.0.0")

# --- Umbral de abstención ---
# Con hnsw:space="cosine" (ver store.py), la distancia va de 0 (idéntico) a 2 (opuesto).
# Si el chunk más parecido recuperado tiene una distancia mayor a este umbral,
# se considera que no hay evidencia suficiente y se responde con abstención
# ANTES de siquiera llamar al modelo generador.
# Configurable por variable de entorno; ajusta el valor según pruebas con tu corpus.
ABSTENTION_DISTANCE_THRESHOLD = float(os.getenv("ABSTENTION_DISTANCE_THRESHOLD", "0.8"))

# --- Inicialización de clientes ---
# El VectorStore no depende de la API key de Google, así que siempre se inicializa.
store = VectorStore()

# embedder y generator SÍ dependen de GOOGLE_API_KEY. Si falta o es inválida,
# no queremos que el proceso entero de FastAPI truene al arrancar: guardamos
# el error y cada endpoint responde de forma controlada en vez de crashear.
try:
    embedder: Optional[GoogleEmbeddingClient] = GoogleEmbeddingClient()
    _embedder_error: Optional[str] = None
except Exception as e:
    embedder = None
    _embedder_error = str(e)

try:
    generator: Optional[GeminiGenerator] = GeminiGenerator()
    _generator_error: Optional[str] = None
except Exception as e:
    generator = None
    _generator_error = str(e)


# --- Schemas ---
class QueryRequest(BaseModel):
    question: str
    top_k: int = 3

class Citation(BaseModel):
    id: Optional[str] = None
    source: Optional[str] = None
    text: str
    score: Optional[float] = None
    page: Optional[int] = None

class QueryResponse(BaseModel):
    answer: str
    abstained: bool
    citations: List[Citation]

class IngestResult(BaseModel):
    filename: str
    status: str
    chunks_created: Optional[int] = None
    detail: Optional[str] = None

class IngestResponse(BaseModel):
    status: str
    documents_indexed: int
    total_chunks_created: int
    details: List[IngestResult]


@app.get("/health")
def health_check():
    try:
        chroma_count = store.collection.count()
        chroma_status = "ok"
    except Exception as e:
        chroma_count = None
        chroma_status = f"error: {e}"

    return {
        "status": "ok",
        "message": "Backend RAG operativo",
        "chroma": chroma_status,
        "chroma_chunks_indexados": chroma_count,
        "embeddings_disponibles": embedder is not None,
        "generacion_disponible": generator is not None,
    }


@app.post("/ingest", response_model=IngestResponse)
async def ingest_file(
    files: List[UploadFile] = File(default=[]),
    paths: Optional[str] = Form(default=None),
):
    """
    Ingesta uno o varios documentos.
    - 'files': uno o varios archivos subidos en el request (PDF, TXT, MD).
    - 'paths' (opcional): rutas ya presentes en el servidor, separadas por comas.
    Al menos uno de los dos debe tener contenido.
    """
    if embedder is None:
        raise HTTPException(
            status_code=503,
            detail=f"Servicio de embeddings no disponible: {_embedder_error}"
        )

    raw_sources: List[tuple] = []  # (filename, content_bytes)

    for file in files:
        filename = file.filename or ""
        content = await file.read()
        raw_sources.append((filename, content))

    if paths:
        for path in [p.strip() for p in paths.split(",") if p.strip()]:
            if not os.path.isfile(path):
                raise HTTPException(status_code=400, detail=f"Ruta no encontrada: {path}")
            with open(path, "rb") as f:
                content = f.read()
            raw_sources.append((os.path.basename(path), content))

    if not raw_sources:
        raise HTTPException(status_code=400, detail="Debes enviar al menos un archivo (files) o una ruta (paths).")

    results: List[IngestResult] = []
    total_chunks = 0

    for filename, content in raw_sources:
        if not filename.lower().endswith((".pdf", ".txt", ".md")):
            results.append(IngestResult(filename=filename, status="error", detail="Formato no soportado. Usa PDF, TXT o MD."))
            continue

        documents = extract_text_from_file(content, filename)
        if not documents:
            results.append(IngestResult(filename=filename, status="error", detail="No se pudo extraer texto del archivo."))
            continue

        chunks = create_chunks(documents)
        if not chunks:
            results.append(IngestResult(filename=filename, status="error", detail="El archivo no contiene texto relevante."))
            continue

        texts = [c["text"] for c in chunks]
        try:
            embeddings = embedder.embed_texts(texts)
        except Exception as e:
            results.append(IngestResult(filename=filename, status="error", detail=f"Error generando embeddings: {e}"))
            continue

        store.add_chunks(chunks, embeddings)
        total_chunks += len(chunks)
        results.append(IngestResult(filename=filename, status="success", chunks_created=len(chunks)))

    documents_indexed = sum(1 for r in results if r.status == "success")

    return IngestResponse(
        status="success" if documents_indexed > 0 else "error",
        documents_indexed=documents_indexed,
        total_chunks_created=total_chunks,
        details=results,
    )


@app.get("/documents")
def list_documents():
    """Devuelve el historial de documentos ingeridos, con su cantidad de chunks."""
    return {"documents": store.list_sources()}


@app.delete("/documents")
def delete_all_documents():
    """
    Borra TODA la colección (no solo los chunks) y la vuelve a crear vacía.
    Útil tras un cambio en la métrica de distancia de Chroma (hnsw:space),
    ya que un simple borrado de chunks no actualiza esa configuración.
    """
    store.reset_collection()
    return {"status": "success", "message": "Colección reiniciada. Vuelve a ingestar tus documentos."}


@app.delete("/documents/{filename}")
def delete_document(filename: str):
    """Elimina un documento (y todos sus chunks) de la base vectorial."""
    deleted = store.delete_by_source(filename)
    if deleted == 0:
        raise HTTPException(status_code=404, detail=f"No se encontró el documento '{filename}'.")
    return {
        "status": "success",
        "filename": filename,
        "chunks_deleted": deleted
    }


@app.post("/query", response_model=QueryResponse)
def query_rag(request: QueryRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="La pregunta no puede estar vacía.")

    if embedder is None:
        return QueryResponse(
            answer=f"No puedo responder: el servicio de embeddings no está disponible ({_embedder_error}).",
            abstained=True,
            citations=[],
        )

    # 1. Embedding de la pregunta + búsqueda en Chroma. Nunca debe propagar un 500:
    #    cualquier fallo (red, cuota de Gemini, etc.) se convierte en abstención.
    try:
        query_emb = embedder.embed_query(request.question)
        retrieved_chunks = store.search(query_emb, top_k=request.top_k)
    except Exception:
        return QueryResponse(
            answer="No tengo evidencia suficiente para responder (ocurrió un error al buscar en la base de conocimiento).",
            abstained=True,
            citations=[],
        )

    # 2. Umbral de abstención por score: si no hay chunks o el mejor está demasiado
    #    lejos semánticamente, no hay evidencia suficiente y ni siquiera llamamos a Gemini.
    if not retrieved_chunks or retrieved_chunks[0]["score"] > ABSTENTION_DISTANCE_THRESHOLD:
        return QueryResponse(
            answer=ABSTENTION_MESSAGE,
            abstained=True,
            citations=[],
        )

    citations = [
        Citation(
            id=c.get("id"),
            source=c.get("metadata", {}).get("source"),
            text=c.get("text"),
            score=c.get("score"),
            page=c.get("metadata", {}).get("page"),
        )
        for c in retrieved_chunks
    ]

    # 3. Generación de la respuesta. Tampoco debe propagar un 500.
    if generator is None:
        return QueryResponse(
            answer=f"No puedo generar una respuesta: el servicio de generación no está disponible ({_generator_error}).",
            abstained=True,
            citations=citations,
        )

    try:
        answer, abstained = generator.generate_response(request.question, retrieved_chunks)
    except Exception:
        return QueryResponse(
            answer="No tengo evidencia suficiente para responder (ocurrió un error al generar la respuesta).",
            abstained=True,
            citations=citations,
        )

    return QueryResponse(answer=answer, abstained=abstained, citations=citations)