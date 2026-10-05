import os
from typing import List, Dict, Any, Tuple
from google import genai
from dotenv import load_dotenv

load_dotenv()

# Mensaje exacto que el modelo debe devolver cuando no hay evidencia suficiente.
# Se usa también en main.py para la abstención por umbral de score.
ABSTENTION_MESSAGE = "No tengo evidencia suficiente en los documentos para responder esa pregunta."


class GeminiGenerator:
    def __init__(self, model_name: str = "gemini-3.6-flash"):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY no encontrada en las variables de entorno.")

        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    def _build_prompt(self, question: str, retrieved_chunks: List[Dict[str, Any]]) -> str:
        context_blocks = []
        for i, c in enumerate(retrieved_chunks, 1):
            source = c.get("metadata", {}).get("source", "desconocido")
            context_blocks.append(f"[{i}] (Fuente: {source})\n{c.get('text', '')}")
        context = "\n\n".join(context_blocks)

        return (
            "Eres un asistente que responde preguntas ÚNICAMENTE con base en el contexto proporcionado. "
            "Responde siempre en español.\n\n"
            "Reglas estrictas:\n"
            "1. Usa solo la información de los fragmentos numerados de abajo. No agregues conocimiento propio ni supuestos.\n"
            "2. Cuando uses información de un fragmento, cita su número entre corchetes (ej. [1], [2]).\n"
            f"3. Si el contexto no contiene información suficiente para responder la pregunta, responde EXACTAMENTE: "
            f"\"{ABSTENTION_MESSAGE}\"\n\n"
            f"Contexto:\n{context}\n\n"
            f"Pregunta: {question}\n\n"
            "Respuesta:"
        )

    def generate_response(
        self, question: str, retrieved_chunks: List[Dict[str, Any]]
    ) -> Tuple[str, bool]:
        """
        Genera una respuesta usando el contexto recuperado.
        Devuelve (respuesta, abstained).
        """
        if not retrieved_chunks:
            return ABSTENTION_MESSAGE, True

        prompt = self._build_prompt(question, retrieved_chunks)

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
        )
        answer_text = (response.text or "").strip()

        if not answer_text:
            return ABSTENTION_MESSAGE, True

        abstained = ABSTENTION_MESSAGE.lower() in answer_text.lower()

        return answer_text, abstained