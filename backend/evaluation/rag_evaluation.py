"""Controlled RAG evaluation, intentionally separate from production requests."""

from __future__ import annotations

import argparse
import json
import tempfile
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import yaml

from app.ai.llm_models.llm_manager import LLMManager
from app.ai.rag.config import RAGConfig
from app.ai.rag.rag_manager import RAGManager


def load_rag_cases(path: Path) -> List[Dict[str, Any]]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or []
    if not isinstance(data, list):
        raise ValueError("Los casos RAG deben ser una lista YAML")
    required = {"id", "question", "section", "expected_document"}
    for item in data:
        missing = required.difference(item)
        if missing:
            raise ValueError(f"Caso RAG incompleto: faltan {sorted(missing)}")
    return data


def run_rag_evaluation(cases: List[Dict[str, Any]], rag_manager: RAGManager, execute: bool = False, llm_manager: LLMManager | None = None) -> List[Dict[str, Any]]:
    records = []
    for case in cases:
        sources = rag_manager.get_relevant_sources(case["question"], case["section"])
        retrieved_documents = {source.get("document") for source in sources}
        recovery_correct = case["expected_document"] in retrieved_documents
        response = None
        generation_status = "NOT_EXECUTED"
        if execute and llm_manager:
            response = llm_manager.ask(question=case["question"], tab=case["section"])
            generation_status = "MANUAL_REVIEW_REQUIRED"
        records.append({
            "id": case["id"], "question": case["question"], "section": case["section"],
            "expected_document": case["expected_document"], "retrieved_fragments": sources,
            "scores": [source.get("score") for source in sources], "response_llm": response,
            "recovery_correct": recovery_correct, "retrieval_status": "CORRECT" if recovery_correct else "RETRIEVAL_FAILURE",
            "generation_status": generation_status if recovery_correct else "NOT_EVALUABLE_RETRIEVAL_FAILURE",
        })
    return records


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("cases", type=Path)
    parser.add_argument("--execute", action="store_true", help="Invoca el proveedor LLM; por defecto solo evalúa recuperación.")
    parser.add_argument("--output", type=Path, default=Path("evaluation/results/rag_evaluation.json"))
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="mga-rag-evaluation-") as index_dir:
        manager = RAGManager(replace(RAGConfig.from_env(), index_dir=Path(index_dir)))
        llm = LLMManager() if args.execute else None
        records = run_rag_evaluation(load_rag_cases(args.cases), manager, args.execute, llm)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps({"executed_at": datetime.now(timezone.utc).isoformat(), "records": records}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{len(records)} casos escritos en {args.output}")


if __name__ == "__main__":
    main()