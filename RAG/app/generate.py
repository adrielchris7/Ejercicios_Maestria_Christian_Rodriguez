import os
from typing import List, Dict, Any, Tuple
from google import genai
from dotenv import load_dotenv

load_dotenv()

class GeminiGenerator:
    def __init__(self, model_name: str = "gemini-3.6-flash"):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY no encontrada en las variables de entorno.")
        
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    def generate_response(
        self, question: str, retrieved_chunks: List[Dict[str, Any]]
    ) -> Tuple[str, bool]:
        """
        Genera una respuesta usando el contexto recuperado.
        Devuelve (respuesta, abstained). abstained=True si no hay contexto suficiente.
        """
        if not retrieved_chunks:
            return (
                "No encontré información suficiente en los documentos para responder eso.",
                True,
            )

        context = "\n\n".join(
            f"[Fuente: {c.get('metadata', {}).get('source', 'desconocida')}] {c.get('text', '')}"
            for c in retrieved_chunks
        )

        prompt = (
            "Responde la pregunta usando ÚNICAMENTE el siguiente contexto. "
            "Si el contexto no contiene la respuesta, dilo explícitamente.\n\n"
            f"Contexto:\n{context}\n\n"
            f"Pregunta: {question}"
        )

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
        )
        answer_text = response.text or ""

        abstained = "no contiene la respuesta" in answer_text.lower() or not answer_text.strip()

        return answer_text, abstained