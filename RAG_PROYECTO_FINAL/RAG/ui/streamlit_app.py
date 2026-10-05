import os
import streamlit as st
import requests

# Configuración de la página
st.set_page_config(
    page_title="RAG System By Christian",
    page_icon="🤖",
    layout="wide"
)

API_BASE_URL = "http://127.0.0.1:8000"

# ---------------------------------------------------------------------------
# Estado de sesión: manejo de múltiples conversaciones
# ---------------------------------------------------------------------------
if "conversations" not in st.session_state:
    st.session_state.conversations = {}
if "current_conv_id" not in st.session_state:
    st.session_state.current_conv_id = None
if "conv_counter" not in st.session_state:
    st.session_state.conv_counter = 0
if "top_k" not in st.session_state:
    st.session_state.top_k = 3


def new_conversation():
    """Crea una conversación nueva y la vuelve la conversación activa."""
    st.session_state.conv_counter += 1
    conv_id = f"conv_{st.session_state.conv_counter}"
    st.session_state.conversations[conv_id] = {
        "title": "Nueva conversación",
        "messages": []  # cada item: {"role", "content", "citations" (opcional), "abstained" (opcional)}
    }
    st.session_state.current_conv_id = conv_id


# Si todavía no hay ninguna conversación (primera carga de la app), crear una
if not st.session_state.conversations:
    new_conversation()

current_conv = st.session_state.conversations[st.session_state.current_conv_id]


def render_citations(citations):
    """Muestra la lista de citas/referencias de una respuesta."""
    if not citations:
        return
    with st.expander("📚 Referencias"):
        for i, cit in enumerate(citations, 1):
            source_name = cit.get("source") or "Desconocido"
            page_num = cit.get("page")
            score = cit.get("score", "N/A")
            page_part = f" (Pág. {page_num})" if page_num is not None else ""
            st.markdown(f"**[{i}] {source_name}**{page_part} — distancia: {score}")
            st.caption(cit.get("text", ""))


# ---------------------------------------------------------------------------
# BARRA LATERAL: logo + historial de conversaciones
# ---------------------------------------------------------------------------
with st.sidebar:
    # --- Logo ---
    LOGO_PATH = "Logo UMY.png"  # <-- reemplaza con la ruta/nombre de tu imagen
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, use_container_width=True)
    else:
        st.markdown(
            """
            <div style="
                height: 80px;
                display: flex;
                align-items: center;
                justify-content: center;
                border: 1px dashed #999;
                border-radius: 8px;
                color: #999;
                font-size: 12px;
                margin-bottom: 10px;
            ">
                Espacio para el logo
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")

    if st.button("➕ Nueva conversación", use_container_width=True):
        new_conversation()
        st.rerun()

    st.markdown("### 🕘 Historial de conversaciones")

    for conv_id in reversed(list(st.session_state.conversations.keys())):
        conv = st.session_state.conversations[conv_id]
        is_current = conv_id == st.session_state.current_conv_id
        label = f"🟢 {conv['title']}" if is_current else conv["title"]
        if st.button(label, key=f"select_{conv_id}", use_container_width=True):
            st.session_state.current_conv_id = conv_id
            st.rerun()

st.title("Sistema RAG - Consulta de Documentos")

tab_chat, tab_settings = st.tabs(["💬 Chat", "⚙️ Configuración"])

# ---------------------------------------------------------------------------
# TAB: CONFIGURACIÓN
# ---------------------------------------------------------------------------
with tab_settings:
    # Estado de la API (clave ausente, Chroma caído, etc.)
    try:
        health = requests.get(f"{API_BASE_URL}/health", timeout=5).json()
        if not health.get("embeddings_disponibles", True):
            st.error("⚠️ El backend no tiene configurada o es inválida GOOGLE_API_KEY (embeddings no disponibles).")
        if not health.get("generacion_disponible", True):
            st.error("⚠️ El backend no puede generar respuestas (revisa GOOGLE_API_KEY).")
        if health.get("chroma") != "ok":
            st.warning(f"⚠️ Problema con la base vectorial: {health.get('chroma')}")
    except Exception:
        st.error("🔴 No se pudo conectar con la API. ¿Está corriendo `uvicorn app.main:app` en el puerto 8000?")

    st.subheader("Parámetros de búsqueda")
    st.session_state.top_k = st.slider(
        "Número de fragmentos a recuperar (top_k)",
        min_value=1, max_value=10, value=st.session_state.top_k
    )

    st.markdown("---")
    st.subheader("📂 Cargar nuevo(s) documento(s)")
    uploaded_files = st.file_uploader(
        "Sube uno o varios archivos (PDF, TXT, MD)",
        type=["pdf", "txt", "md"],
        accept_multiple_files=True,
        key="uploader_settings"
    )
    if uploaded_files and st.button("Procesar e Ingestar Documento(s)"):
        with st.spinner("Procesando documento(s)..."):
            try:
                files_payload = [
                    ("files", (f.name, f.getvalue(), f.type)) for f in uploaded_files
                ]
                response = requests.post(f"{API_BASE_URL}/ingest", files=files_payload)

                if response.status_code == 200:
                    data = response.json()
                    st.success(
                        f"Documentos indexados: {data['documents_indexed']} "
                        f"({data['total_chunks_created']} fragmentos en total)"
                    )
                    for detail in data.get("details", []):
                        if detail["status"] == "success":
                            st.caption(f"✅ {detail['filename']}: {detail['chunks_created']} fragmentos")
                        else:
                            st.caption(f"❌ {detail['filename']}: {detail.get('detail', 'error desconocido')}")
                    st.rerun()
                else:
                    try:
                        error_detail = response.json().get("detail", response.text)
                    except Exception:
                        error_detail = response.text
                    st.error(f"Error ({response.status_code}): {error_detail}")
            except Exception as e:
                st.error(f"Error de conexión con la API: {e}")

    st.markdown("---")
    with st.expander("🧨 Zona de riesgo: reiniciar toda la base vectorial"):
        st.caption(
            "Borra TODA la colección de Chroma (no solo los documentos uno por uno) "
            "y la recrea vacía. Necesario, por ejemplo, tras cambiar la métrica de "
            "distancia del índice. Vas a tener que volver a subir todos tus documentos."
        )
        confirm_reset = st.checkbox("Sí, quiero borrar todo el índice y empezar de cero")
        if st.button("Reiniciar base vectorial", disabled=not confirm_reset):
            try:
                reset_response = requests.delete(f"{API_BASE_URL}/documents")
                if reset_response.status_code == 200:
                    st.success("Base vectorial reiniciada. Ya puedes volver a subir tus documentos.")
                    st.rerun()
                else:
                    st.error(f"No se pudo reiniciar: {reset_response.text}")
            except Exception as e:
                st.error(f"Error de conexión con la API: {e}")

    st.markdown("---")
    st.subheader("📚 Historial de documentos")
    try:
        docs_response = requests.get(f"{API_BASE_URL}/documents")
        if docs_response.status_code == 200:
            documents = docs_response.json().get("documents", [])
            if documents:
                for doc in documents:
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.write(f"📄 {doc['source']}")
                    with col2:
                        st.write(f"{doc['chunks']} fragmentos")
                    with col3:
                        if st.button("🗑️ Eliminar", key=f"del_{doc['source']}"):
                            try:
                                del_response = requests.delete(f"{API_BASE_URL}/documents/{doc['source']}")
                                if del_response.status_code == 200:
                                    st.success(f"'{doc['source']}' eliminado.")
                                    st.rerun()
                                else:
                                    st.error(f"No se pudo eliminar '{doc['source']}'.")
                            except Exception as e:
                                st.error(f"Error de conexión con la API: {e}")
            else:
                st.info("Todavía no se ha subido ningún documento.")
        else:
            st.warning("No se pudo obtener el historial de documentos.")
    except Exception as e:
        st.error(f"Error de conexión con la API: {e}")

# ---------------------------------------------------------------------------
# TAB: CHAT
# ---------------------------------------------------------------------------
with tab_chat:
    for msg in current_conv["messages"]:
        with st.chat_message(msg["role"]):
            if msg["role"] == "assistant" and msg.get("abstained"):
                st.warning("⚠️ Respuesta de abstención")
            st.write(msg["content"])
            render_citations(msg.get("citations"))

    prompt = st.chat_input("Escribe tu pregunta sobre los documentos cargados...")

    if prompt:
        current_conv["messages"].append({"role": "user", "content": prompt})

        if current_conv["title"] == "Nueva conversación":
            current_conv["title"] = prompt[:40] + ("..." if len(prompt) > 40 else "")

        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Buscando en la base vectorial y generando respuesta..."):
                try:
                    payload = {"question": prompt, "top_k": st.session_state.top_k}
                    response = requests.post(f"{API_BASE_URL}/query", json=payload)

                    if response.status_code == 200:
                        result = response.json()
                        answer = result.get("answer", "Sin respuesta disponible.")
                        citations = result.get("citations", [])
                        abstained = result.get("abstained", False)

                        if abstained:
                            st.warning("⚠️ Respuesta de abstención")

                        st.write(answer)
                        render_citations(citations)

                        current_conv["messages"].append({
                            "role": "assistant",
                            "content": answer,
                            "citations": citations,
                            "abstained": abstained
                        })
                    else:
                        try:
                            error_detail = response.json().get("detail", response.text)
                        except Exception:
                            error_detail = response.text
                        error_msg = f"Error en la API ({response.status_code}): {error_detail}"
                        st.error(error_msg)
                        current_conv["messages"].append({"role": "assistant", "content": error_msg})
                except Exception as e:
                    error_msg = f"Error de comunicación con el backend: {e}"
                    st.error(error_msg)
                    current_conv["messages"].append({"role": "assistant", "content": error_msg})