from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any

from app.chunk import extract_text_from_file, create_chunks
from app.embed import GoogleEmbeddingClient
from app.store import VectorStore
from app.generate import GeminiGenerator

app = FastAPI(title="RAG API Backend", version="1.0.0")

# Inicialización de clientes
embedder = GoogleEmbeddingClient()
store = VectorStore()
generator = GeminiGenerator()

# Schemas de Pydantic
class QueryRequest(BaseModel):
    question: str
    top_k: int = 3

class QueryResponse(BaseModel):
    answer: str
    abstained: bool
    sources: List[Dict[str, Any]]

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Backend RAG operativo"}

@app.post("/ingest")
async def ingest_file(file: UploadFile = File(...)):
    filename = file.filename or ""
    if not filename.lower().endswith((".pdf", ".txt", ".md")):
        raise HTTPException(status_code=400, detail="Formato no soportado. Usa PDF, TXT o MD.")
    
    content = await file.read()
    
    # 1. Extraer texto
    documents = extract_text_from_file(content, filename)
    if not documents:
        raise HTTPException(status_code=400, detail="No se pudo extraer texto del archivo.")
    
    # 2. Fragmentar texto
    chunks = create_chunks(documents)
    if not chunks:
        raise HTTPException(status_code=400, detail="El archivo no contiene texto relevante para procesar.")
    
    # 3. Generar embeddings
    texts = [c["text"] for c in chunks]
    embeddings = embedder.embed_texts(texts)
    
    # 4. Guardar en ChromaDB
    store.add_chunks(chunks, embeddings)
    
    return {
        "status": "success",
        "filename": filename,
        "chunks_created": len(chunks)
    }

@app.post("/query", response_model=QueryResponse)
def query_rag(request: QueryRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="La pregunta no puede estar vacía.")

    # 1. Generar embedding de la pregunta
    query_emb = embedder.embed_query(request.question)
    
    # 2. Recuperar k-NN de ChromaDB
    retrieved_chunks = store.search(query_emb, top_k=request.top_k)
    
    # 3. Generar respuesta con Gemini
    answer, abstained = generator.generate_response(request.question, retrieved_chunks)
    
    # Dar formato a las fuentes citadas
    sources = [
        {
            "id": c.get("id"),
            "text": c.get("text"),
            "metadata": c.get("metadata", {}),
            "score": c.get("score")
        }
        for c in retrieved_chunks
    ]
    
    return QueryResponse(
        answer=answer,
        abstained=abstained,
        sources=sources
    )