from typing import List, Dict, Any
from pypdf import PdfReader
import io

def extract_text_from_file(file_bytes: bytes, filename: str) -> List[Dict[str, Any]]:
    """
    Extrae el texto de un archivo (.pdf, .txt, .md).
    Devuelve una lista con el texto y metadata por página/documento.
    """
    pages_data = []
    
    if filename.endswith(".pdf"):
        pdf_file = io.BytesIO(file_bytes)
        reader = PdfReader(pdf_file)
        for page_num, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            if text.strip():
                pages_data.append({
                    "text": text,
                    "page": page_num + 1,
                    "source": filename
                })
    else:
        # Procesamiento para archivos .txt o .md
        text = file_bytes.decode("utf-8", errors="ignore")
        pages_data.append({
            "text": text,
            "page": 1,
            "source": filename
        })
        
    return pages_data

def create_chunks(
    documents: List[Dict[str, Any]], 
    chunk_size_words: int = 300, 
    overlap_words: int = 50
) -> List[Dict[str, Any]]:
    """
    Particiona el texto extraído en chunks basándose en el número de palabras y overlap.
    """
    chunks = []
    chunk_id_counter = 0

    for doc in documents:
        words = doc["text"].split()
        if not words:
            continue

        step = chunk_size_words - overlap_words
        for i in range(0, len(words), step):
            chunk_words = words[i : i + chunk_size_words]
            chunk_text = " ".join(chunk_words)
            
            chunks.append({
                "id": f"{doc['source']}_chunk_{chunk_id_counter}",
                "text": chunk_text,
                "metadata": {
                    "source": doc["source"],
                    "page": doc["page"],
                    "chunk_index": chunk_id_counter
                }
            })
            chunk_id_counter += 1

    return chunks