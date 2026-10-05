import httpx

response = httpx.post(
    "http://127.0.0.1:8000/query",
    json={"question": "¿Qué es el amarillamiento Letal?", "top_k": 3},
    timeout=60.0
)

data = response.json()

print(f"Status code: {response.status_code}")
print(f"Abstención: {data['abstained']}")
print(f"\nRespuesta:\n{data['answer']}")

print(f"\nCitas recuperadas: {len(data['citations'])}")
for i, c in enumerate(data["citations"], 1):
    texto_corto = c["text"][:150] + "..." if len(c["text"]) > 150 else c["text"]
    print(f"\n  [{i}] Fuente: {c['source']} (pág. {c.get('page')}) — score: {c['score']}")
    print(f"      \"{texto_corto}\"")