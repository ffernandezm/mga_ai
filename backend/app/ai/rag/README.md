# RAG Module

Este módulo añade recuperación de contexto desde el documento `manual_conceptual_2015.pdf` para enriquecer las respuestas del LLM.

## Flujo

1. Lectura del PDF con `pypdf`.
2. Normalización de texto.
3. Chunking por ventana deslizante con overlap.
4. Embeddings TF-IDF (`scikit-learn`).
5. Persistencia local del índice en `app/ai/rag/index/`.
6. Retrieval Top-K por similitud coseno (producto punto sobre vectores normalizados).
7. Inyección del contexto recuperado al prompt del LLM.

## Variables de entorno

- `RAG_ENABLED=true|false`: activa/desactiva RAG.
- `RAG_SOURCE_DOCUMENT=/ruta/al/documento.pdf`: documento fuente.
- `RAG_INDEX_DIR=/ruta/al/index`: carpeta de persistencia del índice.
- `RAG_CHUNK_SIZE=1400`: tamaño de chunk (caracteres).
- `RAG_CHUNK_OVERLAP=250`: overlap entre chunks (caracteres).
- `RAG_TOP_K=4`: número de chunks recuperados por consulta.
- `RAG_MIN_SIMILARITY=0.10`: umbral mínimo para aceptar chunks.
- `RAG_MAX_CONTEXT_CHARS=7000`: límite de caracteres enviados al prompt.
- `RAG_AUTO_REINDEX=true|false`: fuerza reconstrucción del índice al iniciar.
- `RAG_EMBEDDING_PROVIDER=tfidf`: proveedor de embedding (actualmente TF-IDF).

## Reindexación

- Por defecto, si no hay índice previo, se crea automáticamente al primer uso.
- Si cambias el PDF, usa `RAG_AUTO_REINDEX=true` o llama al método `rebuild_index()` de `RAGManager`.

## Archivos generados en index

- `chunks.json`: chunks y metadatos.
- `embeddings.npz`: matriz TF-IDF.
- `vectorizer.joblib`: vectorizador entrenado.
