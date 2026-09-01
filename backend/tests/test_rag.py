"""Tests del subsistema RAG (TF-IDF sparse + similitud coseno).

Cubre la regresión del `token_pattern` (vocabulario vacío), el ciclo real de
indexación/persistencia/recarga/búsqueda, la degradación controlada ante
fallos y el determinismo de la configuración.

No invoca ningún proveedor LLM.
"""

from __future__ import annotations

import json
import re
import shutil
import unicodedata
from dataclasses import replace
from pathlib import Path

import pytest

from app.ai.rag.config import DEFAULT_SOURCE_DOCUMENT, RAGConfig
from app.ai.rag.document_processor import DocumentChunk, DocumentProcessor, is_structural_content
from app.ai.rag.embeddings import TfidfEmbeddingModel
from app.ai.rag.rag_manager import RAGManager
from app.ai.rag.section_terms import SECTION_QUERY_TERMS, build_retrieval_query
from app.ai.rag.stopwords import SPANISH_STOPWORDS
from app.ai.rag.vector_store import LocalVectorStore

REAL_PDF = Path(__file__).resolve().parents[1] / "app" / "data" / "Documento_conceptual_2023.pdf"


def _strip_accents(text: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c))

SPANISH_CORPUS = [
    "Metodología General Ajustada para proyectos de inversión pública",
    "La población objetivo del proyecto se define en la evaluación técnica",
    "Los objetivos específicos se derivan de las causas directas del problema",
    "El análisis técnico de la alternativa seleccionada en Bogotá",
]


# ---------------------------------------------------------------------------
# 1. Tokenizer: regresión del token_pattern
# ---------------------------------------------------------------------------

def test_token_pattern_matches_plain_words():
    """Regresión: r"\\\\b\\\\w\\\\w+\\\\b" (doble escape) no matchea texto real."""
    pattern = TfidfEmbeddingModel().vectorizer.token_pattern
    tokens = re.findall(pattern, "Metodología General Ajustada Colombia")
    assert tokens, f"token_pattern {pattern!r} no reconoce palabras normales"
    assert "General" in tokens


def test_token_pattern_equals_sklearn_default():
    from sklearn.feature_extraction.text import TfidfVectorizer

    assert TfidfEmbeddingModel().vectorizer.token_pattern == TfidfVectorizer().token_pattern


def test_broken_double_escaped_pattern_would_fail():
    """Documenta la causa raíz: el patrón con doble escape produce 0 tokens."""
    assert re.findall(r"(?u)\\b\\w\\w+\\b", "Metodología General Ajustada") == []


def test_fit_transform_builds_non_empty_vocabulary():
    model = TfidfEmbeddingModel()
    matrix = model.fit_transform(SPANISH_CORPUS)
    assert len(model.vectorizer.vocabulary_) > 0
    assert matrix.shape[0] == len(SPANISH_CORPUS)
    assert matrix.nnz > 0


@pytest.mark.parametrize("word", ["población", "evaluación", "técnico", "objetivos", "Bogotá"])
def test_accented_spanish_words_are_indexed(word):
    """`strip_accents="unicode"` normaliza tildes: la forma sin tilde debe existir."""
    model = TfidfEmbeddingModel()
    model.fit_transform(SPANISH_CORPUS)
    import unicodedata

    normalized = "".join(
        c for c in unicodedata.normalize("NFKD", word.lower()) if not unicodedata.combining(c)
    )
    assert normalized in model.vectorizer.vocabulary_


def test_tfidf_configuration_unchanged():
    """La arquitectura documentada (TF-IDF sparse, 1-2 gramas) no debe cambiar."""
    vectorizer = TfidfEmbeddingModel().vectorizer
    assert vectorizer.ngram_range == (1, 2)
    assert vectorizer.max_features == 20000
    assert vectorizer.strip_accents == "unicode"
    assert vectorizer.lowercase is True


# ---------------------------------------------------------------------------
# 2. Indexación real con corpus pequeño: build -> persist -> load -> search
# ---------------------------------------------------------------------------

@pytest.fixture()
def small_chunks():
    return [
        DocumentChunk(chunk_id=f"chunk_{i:05d}", text=text, metadata={"chunk_index": i, "start_char": i * 100})
        for i, text in enumerate(SPANISH_CORPUS)
    ]


def test_vector_store_build_persist_reload_and_search(tmp_path, small_chunks):
    store = LocalVectorStore(index_dir=tmp_path)
    assert not store.exists()

    store.build(small_chunks)

    assert store.exists()
    assert (tmp_path / "vectorizer.joblib").stat().st_size > 0
    assert (tmp_path / "embeddings.npz").stat().st_size > 0
    assert (tmp_path / "chunks.json").stat().st_size > 0
    assert len(store._embedding_model.vectorizer.vocabulary_) > 0
    assert store._matrix.shape == (len(small_chunks), len(store._embedding_model.vectorizer.vocabulary_))
    assert store._matrix.nnz > 0

    reloaded = LocalVectorStore(index_dir=tmp_path)
    reloaded.load()
    assert len(reloaded._chunks) == len(small_chunks)
    assert reloaded._matrix.shape == store._matrix.shape

    results = reloaded.similarity_search("objetivos específicos y causas del problema", top_k=2, min_similarity=0.05)
    assert results
    assert results[0]["score"] >= results[-1]["score"]
    assert "objetivos" in results[0]["text"].lower()


def test_similarity_search_respects_min_similarity(tmp_path, small_chunks):
    store = LocalVectorStore(index_dir=tmp_path)
    store.build(small_chunks)

    permissive = store.similarity_search("objetivos", top_k=4, min_similarity=0.0)
    strict = store.similarity_search("objetivos", top_k=4, min_similarity=0.99)
    assert permissive
    assert strict == []


def test_similarity_search_respects_top_k(tmp_path, small_chunks):
    store = LocalVectorStore(index_dir=tmp_path)
    store.build(small_chunks)
    assert len(store.similarity_search("proyecto", top_k=1, min_similarity=0.0)) <= 1


def test_search_without_index_returns_empty(tmp_path):
    assert LocalVectorStore(index_dir=tmp_path).similarity_search("cualquier cosa", top_k=4, min_similarity=0.1) == []


# ---------------------------------------------------------------------------
# 3. Configuración determinista (no depende del orden de imports)
# ---------------------------------------------------------------------------

def test_rag_config_from_env_is_deterministic_without_prior_dotenv(monkeypatch):
    """RAGConfig debe cargar el .env por sí misma, sin depender de llm_manager."""
    for key in ("RAG_CHUNK_SIZE", "RAG_TOP_K", "RAG_MIN_SIMILARITY", "RAG_SOURCE_DOCUMENT"):
        monkeypatch.delenv(key, raising=False)

    config = RAGConfig.from_env()
    assert config.chunk_size >= 300
    assert config.top_k >= 1
    assert isinstance(config.source_document_path, Path)
    assert isinstance(config.index_dir, Path)


def test_rag_config_env_overrides_are_applied(monkeypatch):
    monkeypatch.setenv("RAG_TOP_K", "9")
    monkeypatch.setenv("RAG_MIN_SIMILARITY", "0.42")
    config = RAGConfig.from_env()
    assert config.top_k == 9
    assert config.min_similarity == 0.42


# ---------------------------------------------------------------------------
# 4. Degradación controlada (el chatbot nunca se rompe por el RAG)
# ---------------------------------------------------------------------------

def _config_for(tmp_path, document: Path, **overrides) -> RAGConfig:
    base = RAGConfig.from_env()
    settings = {"source_document_path": document, "index_dir": tmp_path, "auto_reindex": True}
    settings.update(overrides)
    return replace(base, **settings)


def test_missing_source_document_returns_empty_and_logs(tmp_path, caplog):
    config = _config_for(tmp_path, tmp_path / "no_existe.pdf")
    with caplog.at_level("ERROR"):
        assert RAGManager(config).get_relevant_context("árbol de problemas") == ""
    assert "RAG_SOURCE_MISSING" in caplog.text


def test_corrupt_index_rebuilds_when_source_is_available(tmp_path, caplog):
    """Un índice corrupto sin metadata válida se detecta y se reconstruye solo."""
    for name in ("chunks.json", "embeddings.npz", "vectorizer.joblib"):
        (tmp_path / name).write_text("no soy un indice valido", encoding="utf-8")

    config = _config_for(tmp_path, REAL_PDF, auto_reindex=False)
    assert RAGManager(config).get_relevant_context("cadena de valor productos actividades")


def test_corrupt_index_with_matching_metadata_returns_empty_and_logs(prebuilt_index, caplog):
    """Si la metadata coincide pero los artefactos están corruptos, se degrada con log explícito."""
    (prebuilt_index / "embeddings.npz").write_text("corrupto", encoding="utf-8")

    reloaded = RAGManager(_config_for(prebuilt_index, REAL_PDF, auto_reindex=False))
    with caplog.at_level("ERROR"):
        assert reloaded.get_relevant_context("árbol de problemas") == ""
    assert "RAG_INDEX_LOAD_FAILED" in caplog.text


def test_disabled_rag_returns_empty(tmp_path):
    config = _config_for(tmp_path, REAL_PDF, enabled=False)
    assert RAGManager(config).get_relevant_context("árbol de problemas") == ""


def test_prepare_builds_index_without_retrieval(tmp_path):
    manager = RAGManager(_config_for(tmp_path, REAL_PDF, auto_reindex=False))

    assert manager.prepare()
    assert manager.is_ready
    assert manager.vector_store.exists()
    assert manager.vector_store.read_metadata()["source_document"] == REAL_PDF.name


def test_prepare_disabled_rag_is_ready_without_index(tmp_path):
    manager = RAGManager(_config_for(tmp_path, REAL_PDF, enabled=False, auto_reindex=False))

    assert manager.prepare()
    assert manager.is_ready
    assert not manager.vector_store.exists()


def test_empty_query_returns_empty(tmp_path):
    # Query vacía: retorna antes de tocar el índice (no requiere indexar el PDF).
    assert RAGManager(_config_for(tmp_path, REAL_PDF)).get_relevant_context("") == ""


def test_no_relevant_results_returns_empty_context(tmp_path, small_chunks):
    """Sin coincidencias por encima del umbral, el contexto es vacío y controlado."""
    store = LocalVectorStore(index_dir=tmp_path)
    store.build(small_chunks)
    assert store.similarity_search("zzzz qqqq xxxx", top_k=4, min_similarity=0.1) == []


# ---------------------------------------------------------------------------
# 5. Integración local con el PDF real (sin LLM)
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def real_pdf_manager(tmp_path_factory):
    """Indexa el PDF real una sola vez para todo el módulo (la reconstrucción es costosa)."""
    if not REAL_PDF.exists():
        pytest.skip("PDF de referencia no disponible")
    index_dir = tmp_path_factory.mktemp("rag_real_index")
    base = RAGConfig.from_env()
    config = replace(base, source_document_path=REAL_PDF, index_dir=index_dir, auto_reindex=True)
    manager = RAGManager(config)
    manager.rebuild_index()
    return manager


@pytest.fixture()
def prebuilt_index(tmp_path, real_pdf_manager):
    """Copia del índice ya construido: evita reindexar el PDF en cada test."""
    index_dir = tmp_path / "index"
    shutil.copytree(real_pdf_manager.vector_store.index_dir, index_dir)
    return index_dir


@pytest.mark.skipif(not REAL_PDF.exists(), reason="PDF de referencia no disponible")
def test_real_pdf_indexes_and_retrieves(real_pdf_manager):
    store = real_pdf_manager.vector_store
    assert len(store._chunks) > 50
    assert len(store._embedding_model.vectorizer.vocabulary_) > 1000
    assert store._matrix.shape[0] == len(store._chunks)
    assert store._matrix.nnz > 0

    context = real_pdf_manager.get_relevant_context("cadena de valor productos actividades")
    assert context
    assert len(context) <= real_pdf_manager.config.max_context_chars
    assert "cadena de valor" in context.lower()


@pytest.mark.skipif(not REAL_PDF.exists(), reason="PDF de referencia no disponible")
@pytest.mark.parametrize(
    "query,expected_term",
    [
        ("arbol de problemas causas efectos", "causa"),
        ("oferta demanda estudio de necesidades", "demanda"),
        ("localizacion de la alternativa", "localiza"),
        ("cadena de valor productos actividades", "producto"),
    ],
)
def test_real_pdf_retrieval_is_topically_relevant(real_pdf_manager, query, expected_term):
    assert expected_term in real_pdf_manager.get_relevant_context(query).lower()


@pytest.mark.skipif(not REAL_PDF.exists(), reason="PDF de referencia no disponible")
def test_real_pdf_chunking_respects_configured_size():
    config = RAGConfig.from_env()
    chunks = DocumentProcessor().load_and_chunk_pdf(REAL_PDF, config.chunk_size, config.chunk_overlap)
    assert chunks
    assert all(len(chunk.text) <= config.chunk_size for chunk in chunks)
    assert all(chunk.metadata.get("start_char") is not None for chunk in chunks)
    assert all(chunk.metadata.get("source_document") == REAL_PDF.name for chunk in chunks)
    assert all(chunk.metadata.get("page") is not None for chunk in chunks)
    assert all(chunk.metadata.get("chunk_id") == chunk.chunk_id for chunk in chunks)
    assert max(chunk.metadata["page"] for chunk in chunks) == 70
    assert all("3.5 ¿cuáles son los riesgos" not in chunk.text.lower() for chunk in chunks)


# ---------------------------------------------------------------------------
# 6. Fuente documental definitiva (corpus de un solo documento)
# ---------------------------------------------------------------------------

def test_configured_source_is_the_2023_document():
    config = RAGConfig.from_env()
    assert config.source_document_path.name == "Documento_conceptual_2023.pdf"
    assert config.source_document_path.exists()


def test_default_source_is_the_2023_document(monkeypatch):
    monkeypatch.delenv("RAG_SOURCE_DOCUMENT", raising=False)
    assert RAGConfig.from_env().source_document_path == DEFAULT_SOURCE_DOCUMENT
    assert DEFAULT_SOURCE_DOCUMENT.name == "Documento_conceptual_2023.pdf"


def test_relative_source_path_resolves_against_backend_root(monkeypatch):
    monkeypatch.setenv("RAG_SOURCE_DOCUMENT", "app/data/Documento_conceptual_2023.pdf")
    resolved = RAGConfig.from_env().source_document_path
    assert resolved.is_absolute()
    assert resolved == REAL_PDF


@pytest.mark.skipif(not REAL_PDF.exists(), reason="PDF de referencia no disponible")
def test_rag_uses_the_2023_document_in_retrieved_context(prebuilt_index):
    manager = RAGManager(_config_for(prebuilt_index, REAL_PDF, auto_reindex=False))
    context = manager.get_relevant_context("cadena de valor productos actividades")
    assert "Fuente: Documento_conceptual_2023.pdf" in context
    assert "pagina=" in context


# ---------------------------------------------------------------------------
# 7. Stopwords: consultas fuera de dominio no producen similitud artificial
# ---------------------------------------------------------------------------

def test_stopwords_are_configured():
    assert TfidfEmbeddingModel().vectorizer.stop_words == SPANISH_STOPWORDS
    assert "de" in SPANISH_STOPWORDS


@pytest.mark.skipif(not REAL_PDF.exists(), reason="PDF de referencia no disponible")
def test_out_of_domain_query_returns_no_methodological_context(real_pdf_manager):
    """Sin stopwords, "receta de paella valenciana" se reducía al término "de"."""
    assert real_pdf_manager.get_relevant_context("receta de paella valenciana") == ""


# ---------------------------------------------------------------------------
# 8. Filtro de contenido estructural (tabla de contenido / índices)
# ---------------------------------------------------------------------------

def test_structural_content_detection():
    toc = "1 INTRODUCCION ....................................... 9\n2 CONTEXTO ......... 15\n3 MODULO ......... 26"
    prosa = (
        "El problema central corresponde a una situacion negativa existente que afecta a una "
        "poblacion determinada y que debe ser descrita con claridad en su magnitud y alcance."
    )
    assert is_structural_content(toc)
    assert not is_structural_content(prosa)


@pytest.mark.skipif(not REAL_PDF.exists(), reason="PDF de referencia no disponible")
def test_toc_chunks_are_excluded_from_index(real_pdf_manager):
    assert all(not is_structural_content(chunk.text) for chunk in real_pdf_manager.vector_store._chunks)


@pytest.mark.skipif(not REAL_PDF.exists(), reason="PDF de referencia no disponible")
def test_toc_is_not_returned_as_top_result(real_pdf_manager):
    for query in ("oferta demanda estudio de necesidades", "cadena de valor productos actividades"):
        results = real_pdf_manager.vector_store.similarity_search(query, top_k=4, min_similarity=0.10)
        assert results
        assert not is_structural_content(results[0]["text"])


# ---------------------------------------------------------------------------
# 9. Section-aware retrieval (no altera la pregunta del usuario)
# ---------------------------------------------------------------------------

def test_build_retrieval_query_prepends_section_terms():
    question = "¿Qué me falta?"
    enriched = build_retrieval_query(question, "requirements")
    assert enriched.endswith(question)
    assert "oferta demanda" in enriched


def test_build_retrieval_query_is_noop_for_unknown_section():
    question = "¿Qué me falta?"
    assert build_retrieval_query(question, "seccion_inexistente") == question
    assert build_retrieval_query(question, None) == question


@pytest.mark.parametrize("section", list(SECTION_QUERY_TERMS))
def test_every_canonical_section_has_retrieval_terms(section):
    assert SECTION_QUERY_TERMS[section].strip()


@pytest.mark.skipif(not REAL_PDF.exists(), reason="PDF de referencia no disponible")
@pytest.mark.parametrize(
    "section,vague_question,expected_term",
    [
        ("requirements", "¿Qué me falta?", "demanda"),
        ("value_chain", "¿Cómo puedo mejorarlo?", "producto"),
        ("objectives", "¿Esto está bien?", "objetivo"),
    ],
)
def test_section_aware_recovers_context_for_vague_questions(
    real_pdf_manager, section, vague_question, expected_term
):
    raw = real_pdf_manager.get_relevant_context(vague_question)
    enriched = real_pdf_manager.get_relevant_context(vague_question, section=section)
    assert len(enriched) > len(raw)
    assert expected_term in _strip_accents(enriched.lower())


@pytest.mark.skipif(not REAL_PDF.exists(), reason="PDF de referencia no disponible")
def test_user_question_is_never_modified(real_pdf_manager, monkeypatch):
    """El enriquecimiento vive solo en la query de retrieval."""
    seen = {}
    original = real_pdf_manager.vector_store.similarity_search

    def spy(query, top_k, min_similarity):
        seen["retrieval_query"] = query
        return original(query, top_k, min_similarity)

    monkeypatch.setattr(real_pdf_manager.vector_store, "similarity_search", spy)
    question = "¿Qué me falta?"
    real_pdf_manager.get_relevant_context(question, section="requirements")

    assert seen["retrieval_query"] != question
    assert seen["retrieval_query"].endswith(question)


# ---------------------------------------------------------------------------
# 10. Identidad del índice (evita usar un índice de otro corpus/configuración)
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not REAL_PDF.exists(), reason="PDF de referencia no disponible")
def test_index_metadata_matches_the_2023_document(real_pdf_manager):
    metadata = real_pdf_manager.vector_store.read_metadata()

    assert metadata["source_document"] == "Documento_conceptual_2023.pdf"
    assert metadata["source_size"] == REAL_PDF.stat().st_size
    assert len(metadata["source_hash"]) == 64
    assert metadata["corpus_scope"] == DocumentProcessor.CORPUS_SCOPE
    assert metadata["vectorizer"] == "tfidf"
    assert metadata["ngram_range"] == [1, 2]
    assert metadata["chunks"] == metadata["matrix_shape"][0]


@pytest.mark.skipif(not REAL_PDF.exists(), reason="PDF de referencia no disponible")
def test_index_is_rebuilt_when_relevant_metadata_changes(prebuilt_index):
    stale = json.loads((prebuilt_index / "index_metadata.json").read_text(encoding="utf-8"))
    stale["source_hash"] = "0" * 64
    (prebuilt_index / "index_metadata.json").write_text(json.dumps(stale), encoding="utf-8")

    reloaded = RAGManager(_config_for(prebuilt_index, REAL_PDF, auto_reindex=False))
    assert reloaded.get_relevant_context("cadena de valor productos actividades")
    assert reloaded.vector_store.read_metadata()["source_hash"] != "0" * 64


@pytest.mark.skipif(not REAL_PDF.exists(), reason="PDF de referencia no disponible")
def test_index_from_the_2015_manual_is_not_reused(prebuilt_index):
    stale = json.loads((prebuilt_index / "index_metadata.json").read_text(encoding="utf-8"))
    stale["source_document"] = "manual_conceptual_2015.pdf"
    (prebuilt_index / "index_metadata.json").write_text(json.dumps(stale), encoding="utf-8")

    reloaded = RAGManager(_config_for(prebuilt_index, REAL_PDF, auto_reindex=False))
    assert reloaded.get_relevant_context("cadena de valor productos actividades")
    assert reloaded.vector_store.read_metadata()["source_document"] == REAL_PDF.name


@pytest.mark.skipif(not REAL_PDF.exists(), reason="PDF de referencia no disponible")
def test_index_is_rebuilt_when_chunk_size_changes(prebuilt_index):
    assert json.loads((prebuilt_index / "index_metadata.json").read_text(encoding="utf-8"))["chunk_size"] == 1400

    other = RAGManager(_config_for(prebuilt_index, REAL_PDF, auto_reindex=False, chunk_size=1000))
    other.get_relevant_context("cadena de valor productos actividades")
    assert other.vector_store.read_metadata()["chunk_size"] == 1000
