from app.core.database import Base

MODEL_LABELS = {}
TABLE_LABELS = {}

def _rebuild_model_labels() -> None:
    MODEL_LABELS.clear()
    TABLE_LABELS.clear()

    for mapper in Base.registry.mappers:
        model = mapper.class_

        if hasattr(model, "__tablename__"):
            table_info = model.__table__.info or {}

            TABLE_LABELS[model.__tablename__] = {
                "plural": table_info.get("label_plural") or table_info.get("name_plural"),
                "singular": table_info.get("label_singular") or table_info.get("name_singular"),
            }

            MODEL_LABELS[model.__tablename__] = {
                column.name: (
                    column.info.get("name")
                    or column.info.get("label")
                    if column.info
                    else None
                )
                for column in model.__table__.columns
            }


_rebuild_model_labels()


def _resolve_table_name(tab: str) -> str:
    """
    Resuelve claves de relación (p. ej. `localizations`) al __tablename__ real
    (p. ej. `localization`) para encontrar etiquetas correctamente.
    """

    if tab in MODEL_LABELS or tab in TABLE_LABELS:
        return tab

    # Intentar refrescar por si faltan modelos por orden de importación.
    _rebuild_model_labels()
    if tab in MODEL_LABELS or tab in TABLE_LABELS:
        return tab

    candidates = []
    if tab.endswith("ies"):
        candidates.append(tab[:-3] + "y")
    if tab.endswith("es"):
        candidates.append(tab[:-2])
    if tab.endswith("s"):
        candidates.append(tab[:-1])

    for candidate in candidates:
        if candidate in MODEL_LABELS or candidate in TABLE_LABELS:
            return candidate

    return tab


def get_column_label(tab: str, column_name: str) -> str:
    """
    Obtiene el nombre definido en info['name'] (o info['label'] por compatibilidad).
    Si no existe retorna el nombre formateado.
    """

    resolved_tab = _resolve_table_name(tab)

    return (
        MODEL_LABELS.get(resolved_tab, {}).get(column_name)
        or column_name.replace("_", " ").title()
    )


def get_table_label(tab: str, singular: bool = False) -> str:
    """
    Obtiene etiqueta de tabla definida en __table_args__.info.
    Fallback: nombre formateado a partir del tablename.
    """

    resolved_tab = _resolve_table_name(tab)

    labels = TABLE_LABELS.get(resolved_tab, {})

    if singular:
        return labels.get("singular") or tab.replace("_", " ").title()

    return labels.get("plural") or tab.replace("_", " ").title()