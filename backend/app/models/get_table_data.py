from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, selectinload
from app.core.database import SessionLocal
from importlib import import_module
import json
import os
import traceback

router = APIRouter()

# ----------------------------
# Dependencia para la sesión DB
# ----------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ----------------------------
# Serializador seguro de instancias
# ----------------------------
def serialize_instance(obj):
    """Convierte una instancia SQLAlchemy en un dict plano con relaciones directas."""
    data = {}
    for col in obj.__table__.columns:
        data[col.name] = getattr(obj, col.name)

    for rel in obj.__mapper__.relationships:
        related = getattr(obj, rel.key)
        if related is None:
            data[rel.key] = None
        elif isinstance(related, list):
            data[rel.key] = [
                {c.name: getattr(item, c.name) for c in item.__table__.columns}
                for item in related
            ]
        else:
            data[rel.key] = {
                c.name: getattr(related, c.name) for c in related.__table__.columns
            }
    return data


# ----------------------------
# Utilidad para convertir snake_case a PascalCase
# ----------------------------
def snake_to_camel(name: str) -> str:
    """Convierte 'participants_general' -> 'ParticipantsGeneral'."""
    return ''.join(word.capitalize() for word in name.split('_'))


# ----------------------------
# Endpoint principal
# ----------------------------
@router.get("/get_table_data/{model_name}/{project_id}")
def get_table_data(model_name: str, project_id: int, db: Session = Depends(get_db)):
    """
    Obtiene los datos de una tabla específica (modelo) y sus relaciones directas, filtrado por project_id.
    """
    try:
        # 1️⃣ Importar el modelo dinámicamente
        module = import_module(f"app.models.{model_name}")

        # 2️⃣ Obtener la clase del modelo usando PascalCase
        model_class_name = snake_to_camel(model_name)
        model_class = getattr(module, model_class_name, None)

        if model_class is None:
            raise HTTPException(status_code=404, detail=f"Modelo '{model_name}' no encontrado")

        # 3️⃣ Verificar si tiene campo project_id
        if not hasattr(model_class, "project_id"):
            raise HTTPException(
                status_code=400,
                detail=f"El modelo '{model_name}' no tiene campo 'project_id'",
            )

        # 4️⃣ Cargar relaciones directas
        relationships = model_class.__mapper__.relationships
        query = db.query(model_class)
        for rel in relationships:
            query = query.options(selectinload(getattr(model_class, rel.key)))

        # 5️⃣ Filtrar por project_id
        records = query.filter(model_class.project_id == project_id).all()

        # 6️⃣ Serializar datos
        serialized_data = [serialize_instance(record) for record in records]

        # 7️⃣ Construir metadatos de relaciones
        relationships_info = {}
        for rel in relationships:
            fks = []
            for fk in getattr(rel, "_calculated_foreign_keys", []):
                if hasattr(fk, "name"):
                    fks.append(fk.name)
                elif hasattr(fk, "key"):
                    fks.append(fk.key)
                else:
                    fks.append(str(fk))
            relationships_info[rel.key] = {
                "target_model": rel.mapper.class_.__name__,
                "direction": str(rel.direction),
                "foreign_keys": fks,
            }

        # 8️⃣ Columnas principales
        columns = [c.name for c in model_class.__table__.columns]

        result = {
            "table": model_class.__tablename__,
            "model": model_class.__name__,
            "project_id": project_id,
            "columns": columns,
            "relationships": relationships_info,
            "data_count": len(serialized_data),
            "data": serialized_data,
        }

        # 9️⃣ Guardar el resultado JSON
        output_path = os.path.join("app", "data", f"{model_name}.json")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=4)

        return result

    except HTTPException:
        # re-lanzar errores HTTP controlados
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando la tabla '{model_name}': {e}",
        )
