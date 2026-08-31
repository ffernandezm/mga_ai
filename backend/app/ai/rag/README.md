# RAG Module

Este módulo añade recuperación de contexto desde `Documento_conceptual_2023.pdf`, "Lineamientos conceptuales que soportan la Metodología General Ajustada para Colombia" (enero de 2023, versión 2.0), para enriquecer las respuestas del LLM.

## Flujo

1. Lectura del PDF con `pypdf`.
2. Normalización de texto.
3. Selección del corpus desde la introducción hasta finalizar cadena de valor; se excluye la sección 3.5 de riesgos y todo el contenido posterior.
4. Chunking por página y ventana deslizante con overlap, conservando documento, página e identificador del chunk.
5. Embeddings TF-IDF (`scikit-learn`).
6. Persistencia local del índice en `app/ai/rag/index/`.
7. Retrieval Top-K por similitud coseno (producto punto sobre vectores normalizados).
8. Inyección del contexto recuperado al prompt del LLM.

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
- El índice almacena el nombre y hash SHA-256 del PDF, además del alcance del corpus y los parámetros de chunking. Si alguno cambia, se reconstruye automáticamente.
- `RAG_AUTO_REINDEX=true` fuerza una reconstrucción en cada nueva instancia; también puede llamarse al método `rebuild_index()` de `RAGManager`.

## Archivos generados en index

- `chunks.json`: chunks y metadatos.
- `embeddings.npz`: matriz TF-IDF.
- `vectorizer.joblib`: vectorizador entrenado.
- `index_metadata.json`: identidad del PDF, alcance del corpus y estadísticas del índice.
