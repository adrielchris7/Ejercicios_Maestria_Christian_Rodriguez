import streamlit as st
import requests

# Configuración de la página
st.set_page_config(
    page_title="RAG System",
    page_icon="🤖",
    layout="wide"
)

API_BASE_URL = "http://127.0.0.1:8000"

st.title("🤖 Sistema RAG - Consulta de Documentos")
st.markdown("---")

# Barra lateral para carga de documentos
with st.sidebar:
    st.header("📂 Carga de Documentos")
    uploaded_file = st.file_uploader(
        "Sube un archivo (PDF, TXT, MD)", 
        type=["pdf", "txt", "md"]
    )
    
    if uploaded_file is not None:
        if st.button("Procesar e Ingestar Documento"):
            with st.spinner("Procesando documento..."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    response = requests.post(f"{API_BASE_URL}/ingest", files=files)
                    
                    if response.status_code == 200:
                        data = response.json()
                        st.success(f"¡Documento '{data['filename']}' procesado exitosamente! ({data['chunks_created']} fragmentos creados)")
                    else:
                        # Intenta parsear JSON; si falla (ej. en HTML de error 500), muestra response.text
                        try:
                            error_detail = response.json().get('detail', response.text)
                        except Exception:
                            error_detail = response.text
                        st.error(f"Error ({response.status_code}): {error_detail}")
                except Exception as e:
                    st.error(f"Error de conexión con la API: {e}")

# Sección principal para realizar consultas
st.header("🔍 Realizar Consulta")

query = st.text_input("Escribe tu pregunta sobre los documentos cargados:", placeholder="Ej: ¿De qué trata el documento?")
top_k = st.slider("Número de fragmentos a recuperar (top_k)", min_value=1, max_value=10, value=3)

if st.button("Enviar Pregunta") and query:
    with st.spinner("Buscando en la base vectorial y generando respuesta..."):
        try:
            payload = {"question": query, "top_k": top_k}
            response = requests.post(f"{API_BASE_URL}/query", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                
                # Mostrar resultado principal
                if result.get("abstained", False):
                    st.warning("⚠️ **Respuesta de Abstención:**")
                else:
                    st.success("✅ **Respuesta Generada:**")
                
                st.write(result.get("answer", "Sin respuesta disponible."))
                
                st.markdown("---")
                st.subheader("📚 Fuentes Recuperadas")
                
                sources = result.get("sources", [])
                if sources:
                    for i, src in enumerate(sources, 1):
                        score = src.get('score', 'N/A')
                        metadata = src.get('metadata', {})
                        source_name = metadata.get('source', 'Desconocido')
                        page_num = metadata.get('page', 1)
                        
                        with st.expander(f"Fuente [{i}] - Distancia: {score} | Archivo: {source_name} (Pág. {page_num})"):
                            st.write(src.get("text", ""))
                else:
                    st.info("No se recuperaron fragmentos.")
                    
            else:
                try:
                    error_detail = response.json().get('detail', response.text)
                except Exception:
                    error_detail = response.text
                st.error(f"Error en la API ({response.status_code}): {error_detail}")
        except Exception as e:
            st.error(f"Error de comunicación con el backend: {e}")