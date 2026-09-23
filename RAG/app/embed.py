import os
from typing import List
from google import genai
from google.genai.types import EmbedContentConfig
from dotenv import load_dotenv

load_dotenv()

class GoogleEmbeddingClient:
    def __init__(self, model_name: str = "gemini-embedding-001"):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY no se encuentra en el archivo .env")
        
        # Forzamos la versión 'v1' de la API REST para evitar el 404 de v1beta
        self.client = genai.Client(
            api_key=api_key,
            http_options={'api_version': 'v1'}
        )
        self.model_name = model_name.replace("models/", "")

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Genera embeddings para una lista de fragmentos (documentos a indexar)."""
        if not texts:
            return []
        
        embeddings = []
        for text in texts:
            response = self.client.models.embed_content(
                model=self.model_name,
                contents=text,
                config=EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT"),
            )
            embeddings.append(response.embeddings[0].values)
            
        return embeddings

    def embed_query(self, query: str) -> List[float]:
        """Genera embedding para una consulta de búsqueda."""
        response = self.client.models.embed_content(
            model=self.model_name,
            contents=query,
            config=EmbedContentConfig(task_type="RETRIEVAL_QUERY"),
        )
        return response.embeddings[0].values