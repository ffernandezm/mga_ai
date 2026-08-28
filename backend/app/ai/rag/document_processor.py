"""Utilidades para lectura y chunking del documento fuente."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import List

from pypdf import PdfReader


@dataclass
class DocumentChunk:
    """Representa un chunk del documento con metadatos básicos."""

    chunk_id: str
    text: str
    metadata: dict


_TOC_TITLE = re.compile(
    r"(tabla\s+de\s+contenido|indice\s+de\s+(ilustraciones|tablas|graficos|contenido)|"
    r"lista\s+de\s+(ilustraciones|tablas))",
    re.IGNORECASE,
)
_DOT_LEADER = re.compile(r"\.{4,}\s*\d*")


def _strip_accents(text: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c))


def is_structural_content(text: str) -> bool:
    """Detecta tablas de contenido, índices y tablas numéricas.

    El filtro es por contenido (dot leaders, referencias a página, densidad de
    puntos) y no por número de página: la introducción sí aporta contenido útil.
    """
    plain = _strip_accents(text)
    lines = [line.strip() for line in plain.splitlines() if line.strip()]
    if not lines:
        return True

    dot_leader_lines = sum(1 for line in lines if _DOT_LEADER.search(line))
    page_ref_lines = sum(1 for line in lines if re.search(r"\.{2,}\s*\d+\s*$|\s\d{1,3}\s*$", line))

    if dot_leader_lines / len(lines) >= 0.30:
        return True
    if _TOC_TITLE.search(plain) and page_ref_lines / len(lines) >= 0.40:
        return True
    # Densidad de puntos muy alta: dot leaders o tablas numéricas con separador de miles.
    if plain.count(".") / max(len(plain), 1) >= 0.15:
        return True
    return False


class DocumentProcessor:
    """Lee documentos y los divide en chunks con overlap."""

    @staticmethod
    def extract_text_from_pdf(file_path: Path) -> str:
        reader = PdfReader(str(file_path))
        page_texts = []
        for index, page in enumerate(reader.pages, start=1):
            extracted = (page.extract_text() or "").strip()
            if extracted:
                page_texts.append(f"[PAGINA {index}]\n{extracted}")
        return "\n\n".join(page_texts)

    @staticmethod
    def _normalize_text(text: str) -> str:
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"[\t ]{2,}", " ", text)
        return text.strip()

    def split_text(self, text: str, chunk_size: int, chunk_overlap: int) -> List[DocumentChunk]:
        normalized = self._normalize_text(text)
        if not normalized:
            return []

        chunks: List[DocumentChunk] = []
        start = 0
        text_len = len(normalized)
        chunk_index = 0

        while start < text_len:
            max_end = min(start + chunk_size, text_len)
            end = max_end

            if max_end < text_len:
                soft_break = normalized.rfind("\n", start + int(chunk_size * 0.6), max_end)
                sentence_break = normalized.rfind(".", start + int(chunk_size * 0.6), max_end)
                end = max(soft_break, sentence_break)
                if end <= start:
                    end = max_end

            chunk_text = normalized[start:end].strip()
            if chunk_text:
                chunks.append(
                    DocumentChunk(
                        chunk_id=f"chunk_{chunk_index:05d}",
                        text=chunk_text,
                        metadata={
                            "chunk_index": chunk_index,
                            "start_char": start,
                            "end_char": end,
                        },
                    )
                )
                chunk_index += 1

            if end >= text_len:
                break

            start = max(end - chunk_overlap, 0)

        return chunks

    def load_and_chunk_pdf(self, file_path: Path, chunk_size: int, chunk_overlap: int) -> List[DocumentChunk]:
        text = self.extract_text_from_pdf(file_path)
        chunks = self.split_text(text=text, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        return [chunk for chunk in chunks if not is_structural_content(chunk.text)]
