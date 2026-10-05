import chromadb
from typing import List, Dict, Any

class VectorStore:
    def __init__(self, persist_path: str = "chroma", collection_name: str = "rag_collection"):
        self.client = chromadb.PersistentClient(path=persist_path)
        # Fijamos explícitamente la métrica a "cosine" para que el score (distancia)
        # sea interpretable en un rango conocido (0 = idéntico, 2 = opuesto) y así
        # poder usar un umbral de abstención consistente en main.py.
        #
        # IMPORTANTE: si ya tenías una colección creada con la métrica por defecto
        # (l2), esta metadata NO se aplica retroactivamente. Borra la carpeta
        # "chroma/" y vuelve a ingestar tus documentos para que tome efecto.
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def add_chunks(self, chunks: List[Dict[str, Any]], embeddings: List[List[float]]):
        """Guarda chunks y sus vectores en ChromaDB."""
        if not chunks:
            return

        ids = [c["id"] for c in chunks]
        documents = [c["text"] for c in chunks]
        metadatas = [c["metadata"] for c in chunks]

        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )

    def search(self, query_embedding: List[float], top_k: int = 3) -> List[Dict[str, Any]]:
        """Busca los top_k vecinos más cercanos dado el embedding de la pregunta."""
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )

        formatted_results = []
        if results and results["documents"] and results["documents"][0]:
            for i in range(len(results["documents"][0])):
                score = results["distances"][0][i] if results.get("distances") else 0.0
                formatted_results.append({
                    "id": results["ids"][0][i],
                    "text": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "score": round(score, 4)
                })

        return formatted_results

    def list_sources(self) -> List[Dict[str, Any]]:
        """
        Devuelve la lista de documentos únicos ingeridos (agrupados por 'source'),
        junto con la cantidad de chunks que tiene cada uno.
        """
        results = self.collection.get(include=["metadatas"])
        counts: Dict[str, int] = {}

        metadatas = results.get("metadatas") or []
        for meta in metadatas:
            source = meta.get("source", "desconocido")
            counts[source] = counts.get(source, 0) + 1

        return [
            {"source": source, "chunks": n}
            for source, n in sorted(counts.items())
        ]

    def delete_by_source(self, source: str) -> int:
        """
        Elimina todos los chunks pertenecientes a un documento (por su nombre de archivo).
        Devuelve el número de chunks eliminados.
        """
        existing = self.collection.get(where={"source": source}, include=[])
        ids = existing.get("ids", [])

        if ids:
            self.collection.delete(ids=ids)

        return len(ids)

    def reset_collection(self):
        """
        Elimina la colección COMPLETA (no solo sus chunks) y la vuelve a crear vacía,
        con la métrica de distancia definida en __init__. Útil para que un cambio de
        métrica (por ejemplo l2 -> cosine) tome efecto de verdad, sin tener que borrar
        la carpeta 'chroma/' a mano.
        """
        name = self.collection.name
        self.client.delete_collection(name=name)
        self.collection = self.client.get_or_create_collection(
            name=name,
            metadata={"hnsw:space": "cosine"}
        )