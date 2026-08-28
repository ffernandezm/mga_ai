"""Runner de la evaluación controlada.

Modo por defecto: `--dry-run` (construye los prompts y NO invoca a ningún
proveedor). Las llamadas al proveedor requieren `--execute` explícito.

Las variantes A/B/C comparten exactamente el mismo prompt general, el mismo
prompt de sección, la misma pregunta, el mismo historial y la misma
configuración de generación. La única diferencia es el contexto disponible.
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from typing import Any, Dict, List, Optional

from app.ai.context.context_manager import ContextManager, render_semantic_context
from app.ai.llm_models.llm_manager import LLMManager
from app.ai.llm_models.token_diagnostics import TOKEN_METHOD, count_tokens
from app.ai.rag.rag_manager import RAGManager

from .fixtures import FIXTURES, build_case_session
from .loader import load_cases_by_section
from .schema import VARIANTS, EvaluationCase, RunRecord, TokenUsage

RESULTS_DIR = Path(__file__).resolve().parent / "results" / "runs"

# Los primeros 9 casos se ejecutan sin historial para aislar el efecto del
# contexto estructurado y del RAG.
EMPTY_CHAT_HISTORY: List[Dict[str, Any]] = []

_MODEL_ENV_BY_PROVIDER = {"groq": "GROQ_MODEL", "openai": "OPENAI_MODEL", "gemini": "GOOGLE_MODEL"}


def _build_llm_manager(execute: bool) -> LLMManager:
    """LLMManager real en `--execute`; sin modelo inicializado en dry-run."""
    if execute:
        return LLMManager()

    manager = LLMManager.__new__(LLMManager)
    manager.llm_provider = os.getenv("LLM_PROVIDER", "groq").lower()
    manager.templates = manager._load_templates()
    manager.rag_manager = RAGManager()
    manager.context_manager = ContextManager()
    manager.max_chat_history_messages = max(int(os.getenv("LLM_MAX_CHAT_HISTORY_MESSAGES", "6")), 1)
    manager.max_project_context_chars = max(int(os.getenv("LLM_MAX_PROJECT_CONTEXT_CHARS", "12000")), 1000)
    manager.model = None
    return manager


def _model_descriptor(manager: LLMManager, execute: bool) -> Dict[str, Any]:
    provider = manager.llm_provider
    env_key = _MODEL_ENV_BY_PROVIDER.get(provider, "")
    return {
        "provider": provider,
        "name": os.getenv(env_key, "") if env_key else "",
        "temperature": 0.7,
        "initialized": execute,
    }


def build_prompt_parts(
    manager: LLMManager,
    case: EvaluationCase,
    variant: str,
    project_context: str,
    rag_context: str,
) -> Dict[str, Any]:
    """Compone el prompt final replicando la composición de `LLMManager.ask`."""
    template = manager.get_prompt_template(case.section)
    history_text = manager._build_chat_context(EMPTY_CHAT_HISTORY) if EMPTY_CHAT_HISTORY else ""

    project_context, rag_context = manager._prepare_contexts_for_prompt(project_context, rag_context)

    full_prompt = template.format(
        project_context=project_context,
        rag_context=rag_context,
        chat_history=history_text,
        question=case.question,
    )
    return {
        "variant": variant,
        "full_prompt": full_prompt,
        "project_context": project_context,
        "rag_context": rag_context,
        "chat_history": history_text,
        "question": case.question,
    }


def build_case_contexts(manager: LLMManager, case: EvaluationCase) -> Dict[str, Any]:
    """Construye el contexto por el flujo real de producción, en BD aislada."""
    db = build_case_session()
    try:
        project_id = FIXTURES[case.fixture](db)

        context_start = perf_counter()
        semantic_context = ContextManager().build_semantic_context(
            db=db, project_id=project_id, section=case.section, mode="generation"
        )
        project_context = render_semantic_context(semantic_context)
        context_ms = (perf_counter() - context_start) * 1000

        rag_start = perf_counter()
        rag_context = manager.rag_manager.get_relevant_context(case.question, section=case.section)
        rag_ms = (perf_counter() - rag_start) * 1000

        return {
            "project_id": project_id,
            "project_context": project_context,
            "rag_context": rag_context,
            "context_ms": context_ms,
            "rag_ms": rag_ms,
        }
    finally:
        db.close()


def _contexts_for_variant(variant: str, built: Dict[str, Any]) -> tuple[str, str]:
    if variant == "A":
        return "", ""
    if variant == "B":
        return built["project_context"], ""
    return built["project_context"], built["rag_context"]


def _rag_descriptor(manager: LLMManager) -> Dict[str, Any]:
    config = manager.rag_manager.config
    metadata = manager.rag_manager.vector_store.read_metadata() or {}
    return {
        "rag_enabled": config.enabled,
        "source_document": metadata.get("source_document", config.source_document_path.name),
        "index_hash": metadata.get("source_hash"),
        "chunk_size": config.chunk_size,
        "chunk_overlap": config.chunk_overlap,
        "top_k": config.top_k,
        "min_similarity": config.min_similarity,
        "max_context_chars": config.max_context_chars,
        "section_aware": True,
    }


def _extract_usage(response: Any, prompt_text: str) -> TokenUsage:
    """Prioriza los tokens reportados por el proveedor; si no hay, estima."""
    usage = getattr(response, "usage_metadata", None)
    if usage:
        return TokenUsage(
            source="provider",
            prompt=usage.get("input_tokens"),
            completion=usage.get("output_tokens"),
            total=usage.get("total_tokens"),
            method="provider usage_metadata",
        )
    return TokenUsage(source="estimated_tiktoken", prompt=count_tokens(prompt_text), method=TOKEN_METHOD)


def run_case(
    manager: LLMManager,
    case: EvaluationCase,
    variants: List[str],
    run_id: str,
    execute: bool,
) -> List[RunRecord]:
    built = build_case_contexts(manager, case)
    model = _model_descriptor(manager, execute)
    config = _rag_descriptor(manager)
    config["variant_isolation"] = "mismo template, misma pregunta, mismo historial; solo cambia el contexto"

    records: List[RunRecord] = []
    for variant in variants:
        project_context, rag_context = _contexts_for_variant(variant, built)
        prompt = build_prompt_parts(manager, case, variant, project_context, rag_context)

        record = RunRecord(
            run_id=run_id,
            case_id=case.id,
            section=case.section,
            case_type=case.type,
            variant=variant,
            executed=execute,
            model=model,
            config=config,
            prompt=prompt,
            timing={
                "context_ms": round(built["context_ms"], 1),
                "rag_ms": round(built["rag_ms"], 1) if variant == "C" else 0.0,
            },
        )

        if execute:
            try:
                llm_start = perf_counter()
                response = manager.model.invoke(prompt["full_prompt"])
                record.timing["llm_ms"] = round((perf_counter() - llm_start) * 1000, 1)
                record.response = getattr(response, "content", str(response))
                record.tokens = _extract_usage(response, prompt["full_prompt"]).as_dict()
            except Exception as exc:  # una falla no debe abortar la corrida completa
                record.error = {"type": type(exc).__name__, "message": str(exc)}
        else:
            record.tokens = TokenUsage(
                source="estimated_tiktoken",
                prompt=count_tokens(prompt["full_prompt"]),
                method=TOKEN_METHOD,
            ).as_dict()

        records.append(record)
    return records


def write_jsonl(records: List[RunRecord], output: Path) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("a", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record.as_dict(), ensure_ascii=False) + "\n")
    return output


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Evaluación controlada del asistente MGA (dry-run por defecto).")
    parser.add_argument("--sections", default="", help="Secciones separadas por coma (por defecto: todas)")
    parser.add_argument("--variants", default="A,B,C", help="Variantes a construir")
    parser.add_argument("--provider", default="", help="Sobrescribe LLM_PROVIDER solo para esta corrida")
    parser.add_argument("--model", default="", help="Sobrescribe el modelo del proveedor solo para esta corrida")
    parser.add_argument("--execute", action="store_true", help="Invoca al proveedor (por defecto NO se invoca)")
    parser.add_argument("--output", default="", help="Ruta del JSONL de salida")
    args = parser.parse_args(argv)

    if args.provider:
        os.environ["LLM_PROVIDER"] = args.provider.lower()
    if args.model:
        provider = os.environ.get("LLM_PROVIDER", "groq").lower()
        env_key = _MODEL_ENV_BY_PROVIDER.get(provider)
        if env_key:
            os.environ[env_key] = args.model

    variants = [v.strip().upper() for v in args.variants.split(",") if v.strip()]
    invalid = [v for v in variants if v not in VARIANTS]
    if invalid:
        parser.error(f"variantes no válidas: {invalid}")

    sections = [s for s in args.sections.split(",") if s.strip()]
    cases = load_cases_by_section(sections)
    if not cases:
        parser.error("no hay casos que coincidan con el filtro")

    manager = _build_llm_manager(args.execute)
    run_id = f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}_{manager.llm_provider}"
    output = Path(args.output) if args.output else RESULTS_DIR / f"{run_id}.jsonl"

    mode = "EXECUTE (invoca proveedor)" if args.execute else "DRY-RUN (no invoca proveedor)"
    print(f"run_id={run_id} | modo={mode} | casos={len(cases)} | variantes={','.join(variants)}")

    all_records: List[RunRecord] = []
    for case in cases:
        records = run_case(manager, case, variants, run_id, args.execute)
        all_records.extend(records)
        summary = " ".join(
            f"{r.variant}:{r.tokens['prompt'] if r.tokens else '?'}t" + ("!" if r.error else "")
            for r in records
        )
        print(f"  {case.id:<42} {summary}")

    write_jsonl(all_records, output)
    print(f"\n{len(all_records)} registros -> {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
