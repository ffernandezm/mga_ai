"""Orden, etiquetas y dependencias bloqueantes de las secciones MGA."""

SECTION_ORDER = [
    "development_plans",
    "problems",
    "participants",
    "population",
    "objectives",
    "alternatives",
    "requirements",
    "technical_analysis",
    "localization",
    "value_chain",
]

SECTION_LABELS = {
    "development_plans": "Plan de Desarrollo",
    "problems": "Problemática",
    "participants": "Participantes",
    "population": "Población",
    "objectives": "Objetivos",
    "alternatives": "Alternativas",
    "requirements": "Necesidades",
    "technical_analysis": "Análisis Técnico",
    "localization": "Localización",
    "value_chain": "Cadena de Valor",
}

SECTION_PREREQUISITES = {
    "development_plans": [],
    "problems": ["development_plans"],
    "participants": ["problems"],
    "population": ["problems"],
    "objectives": ["problems"],
    "alternatives": ["problems", "objectives"],
    "requirements": ["population", "objectives", "alternatives"],
    "technical_analysis": ["alternatives", "requirements"],
    "localization": ["population", "alternatives", "requirements", "technical_analysis"],
    "value_chain": ["objectives", "alternatives", "requirements"],
}