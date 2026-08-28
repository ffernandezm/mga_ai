"""Stopwords en español para el vectorizador TF-IDF del RAG.

Lista explícita y controlada (sin dependencias adicionales). Evita que una
consulta fuera de dominio quede representada únicamente por palabras vacías:
sin esta lista, "receta de paella valenciana" produce un vector cuyo único
término es "de", que coincide con casi todo el corpus.
"""

from __future__ import annotations

# Escritas sin tildes a propósito: el vectorizador usa strip_accents="unicode",
# por lo que compara contra tokens ya normalizados.
SPANISH_STOPWORDS: list[str] = [
    "a", "al", "algo", "algunas", "algunos", "ante", "antes", "aquel", "aquella", "aquellos",
    "asi", "aun", "aunque", "cada", "como", "con", "contra", "cual", "cuales", "cuando",
    "cuanto", "de", "del", "desde", "donde", "dos", "e", "el", "ella", "ellas", "ellos",
    "en", "entre", "era", "eran", "es", "esa", "esas", "ese", "eso", "esos", "esta",
    "estan", "estas", "este", "esto", "estos", "fue", "fueron", "ha", "han", "hasta",
    "hay", "la", "las", "le", "les", "lo", "los", "mas", "me", "mi", "mientras", "misma",
    "mismo", "mucho", "muy", "ni", "no", "nos", "o", "otra", "otras", "otro", "otros",
    "para", "pero", "por", "porque", "pues", "que", "quien", "se", "segun", "ser",
    "si", "sin", "sobre", "solo", "son", "su", "sus", "tal", "tambien", "tanto", "te",
    "tiene", "todo", "todos", "tras", "un", "una", "uno", "unos", "y", "ya",
]
