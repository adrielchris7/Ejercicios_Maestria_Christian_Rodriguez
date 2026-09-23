# Pasos para poder iniciar el sistema RAG de manera correcta.

## Pasos para la inicialización detro de la terminal.
- Terminal 1 
```
uvicorn app.main:app --reload --port 8000

```

- Terminal 2 
```
.\venv\Scripts\Activate
streamlit run ui/streamlit_app.py

```


Para poder abrir la UI
