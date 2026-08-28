"""Genera la plantilla CSV de calificación manual y el comparativo A/B/C.

La calificación humana vive SIEMPRE en un CSV aparte: nunca se escribe dentro
del JSONL de ejecución.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from statistics import mean
from typing import Dict, List, Optional

RESULTS_DIR = Path(__file__).resolve().parent / "results"
SCORING_DIR = RESULTS_DIR / "scoring"

CRITERIA = ["C1", "C2", "C3", "C4", "C5", "C6", "C7"]
SCORING_COLUMNS = [
    "case_id",
    "variant",
    "run_id",
    *CRITERIA,
    "avg",
    "failed",
    "blocking_issues",
    "reviewer",
    "notes",
]


def read_runs(jsonl_path: Path) -> List[Dict]:
    with jsonl_path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def build_scoring_template(jsonl_path: Path, output: Optional[Path] = None) -> Path:
    """Crea el CSV vacío que el evaluador humano completa."""
    runs = read_runs(jsonl_path)
    target = output or SCORING_DIR / f"{jsonl_path.stem}_scoring.csv"
    target.parent.mkdir(parents=True, exist_ok=True)

    with target.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=SCORING_COLUMNS)
        writer.writeheader()
        for run in runs:
            row = {column: "" for column in SCORING_COLUMNS}
            row.update(case_id=run["case_id"], variant=run["variant"], run_id=run["run_id"])
            writer.writerow(row)
    return target


def summarize_scoring(csv_path: Path) -> Dict[str, Dict[str, float]]:
    """Promedio por criterio y por variante. C5=1 marca el caso como failed."""
    with csv_path.open(encoding="utf-8") as handle:
        rows = [row for row in csv.DictReader(handle) if row.get("C1")]

    by_variant: Dict[str, List[Dict]] = {}
    for row in rows:
        by_variant.setdefault(row["variant"], []).append(row)

    summary: Dict[str, Dict[str, float]] = {}
    for variant, variant_rows in sorted(by_variant.items()):
        scores = {c: mean(float(r[c]) for r in variant_rows) for c in CRITERIA}
        scores["avg"] = mean(scores[c] for c in CRITERIA)
        scores["failed"] = sum(1 for r in variant_rows if float(r["C5"]) == 1)
        scores["n"] = len(variant_rows)
        summary[variant] = scores
    return summary


def print_comparison(summary: Dict[str, Dict[str, float]]) -> None:
    if not summary:
        print("El CSV de calificación aún no tiene filas completadas.")
        return

    header = f"{'Var':<5}{'n':>4}" + "".join(f"{c:>6}" for c in CRITERIA) + f"{'AVG':>7}{'failed':>8}"
    print(header)
    print("-" * len(header))
    for variant, scores in summary.items():
        line = f"{variant:<5}{int(scores['n']):>4}" + "".join(f"{scores[c]:>6.2f}" for c in CRITERIA)
        print(line + f"{scores['avg']:>7.2f}{int(scores['failed']):>8}")

    if "A" in summary and "B" in summary:
        print(f"\ndelta B-A (aporte del contexto estructurado): {summary['B']['avg'] - summary['A']['avg']:+.2f}")
    if "B" in summary and "C" in summary:
        print(f"delta C-B (aporte del RAG):                   {summary['C']['avg'] - summary['B']['avg']:+.2f}")


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Plantilla de calificación y comparativo A/B/C.")
    parser.add_argument("jsonl", help="Ruta del JSONL de ejecuciones")
    parser.add_argument("--scoring", default="", help="CSV de calificación ya diligenciado (para el comparativo)")
    args = parser.parse_args(argv)

    if args.scoring:
        print_comparison(summarize_scoring(Path(args.scoring)))
        return 0

    target = build_scoring_template(Path(args.jsonl))
    print(f"Plantilla de calificación creada: {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
