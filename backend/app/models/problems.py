from ..ai.config.config import GOOGLE_API_KEY
from fastapi import APIRouter, Depends, HTTPException, Body, Query
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session, relationship
from app.core.database import Base, SessionLocal
from sqlalchemy import Column, Integer, Text, JSON, ForeignKey
from sqlalchemy.orm import joinedload
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json

# Import local para evitar circular imports
from app.models.direct_effects import DirectEffect, DirectEffectCreate, DirectEffectResponse
from app.models.direct_causes import DirectCause, DirectCauseCreate, DirectCauseResponse
from app.models.indirect_effects import IndirectEffect
from app.models.indirect_causes import IndirectCause
from app.models.objectives_causes import ObjectivesCauses
from app.models.objectives import Objectives

from ..ai.llm_models.gemini_llm import ChatBotModel
from app.ai.main import main

# Conexión a la DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Modelo en SQLAlchemy
class Problems(Base):
    __tablename__ = "problems"

    id = Column(Integer, primary_key=True, index=True)
    central_problem = Column(Text, nullable=False, default="")
    current_description = Column(Text, nullable=False, default="")
    magnitude_problem = Column(Text, nullable=False, default="")
    # Campos JSON opcionales
    problem_tree_json = Column(JSON, nullable=True)
    
    # Relación con Project (CORREGIDO)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, unique=True)
    project = relationship(
        "Project",
        back_populates="problem",
        foreign_keys=[project_id]   # 👈 aclaramos la FK
    )
    
    direct_effects = relationship("DirectEffect", back_populates="problem", cascade="all, delete-orphan")
    direct_causes = relationship("DirectCause", back_populates="problem", cascade="all, delete-orphan")

    
    @property
    def chatbot(self):
        """Siempre devuelve un ChatBotModel válido."""
        return ChatBotModel(api_key=GOOGLE_API_KEY)

# Esquema Pydantic
class ProblemBase(BaseModel):
    project_id: int
    central_problem: Optional[str] = ""
    current_description: Optional[str] = ""
    magnitude_problem: Optional[str] = ""
    problem_tree_json: Optional[Dict[str, Any]] = None

class ProblemCreate(ProblemBase):
    direct_effects: List[DirectEffectCreate] = []
    direct_causes: List[DirectCauseCreate] = []

class ProblemResponse(ProblemBase):
    id: int
    direct_effects: List[DirectEffectResponse] = []
    direct_causes: List[DirectCauseResponse] = []

    class Config:
        from_attributes = True

# Rutas de FastAPI
router = APIRouter()



@router.post("/", response_model=ProblemResponse)
def create_problem(problem: ProblemCreate, db: Session = Depends(get_db)):
    # Import local para evitar circular imports
    from app.models.project import Project
    
    # Verificar que el proyecto exista
    existing_problem = db.query(Problems).filter(Problems.project_id == problem.project_id).first()
    if existing_problem:
        raise HTTPException(status_code=400, detail="El proyecto ya tiene un problema asignado")
    
    db_problem = Problems(
        project_id=problem.project_id,  # Añade project_id
        central_problem=problem.central_problem,
        current_description=problem.current_description,
        magnitude_problem=problem.magnitude_problem
    )
    db.add(db_problem)
    db.commit()
    db.refresh(db_problem)

    # Sincronizar central_problem con general_problem de Objectives
    db_objective = db.query(Objectives).filter(Objectives.project_id == problem.project_id).first()
    if db_objective and problem.central_problem:
        db_objective.general_problem = problem.central_problem
        db.commit()

    problem_tree = {
        "central_problem": db_problem.central_problem,
        "current_description": db_problem.current_description,
        "magnitude_problem": db_problem.magnitude_problem,
        "direct_effects": [],
        "direct_causes": [],
        
    }

    # Agregar efectos directos e indirectos
    for effect in problem.direct_effects:
        db_effect = DirectEffect(description=effect.description, problem_id=db_problem.id)
        db.add(db_effect)
        db.commit()
        db.refresh(db_effect)

        indirect_effects = []
        for indirect_effect in effect.indirect_effects:
            db_indirect_effect = IndirectEffect(description=indirect_effect.description, direct_effect_id=db_effect.id)
            db.add(db_indirect_effect)
            indirect_effects.append({"description": db_indirect_effect.description})

        problem_tree["direct_effects"].append({
            "description": db_effect.description,
            "indirect_effects": indirect_effects
        })

    # Agregar causas directas e indirectas
    for cause in problem.direct_causes:
        db_cause = DirectCause(description=cause.description, problem_id=db_problem.id)
        db.add(db_cause)
        db.commit()
        db.refresh(db_cause)

        indirect_causes = []
        for indirect_cause in cause.indirect_causes:
            db_indirect_cause = IndirectCause(description=indirect_cause.description, direct_cause_id=db_cause.id)
            db.add(db_indirect_cause)
            indirect_causes.append({"description": db_indirect_cause.description})

        problem_tree["direct_causes"].append({
            "description": db_cause.description,
            "indirect_causes": indirect_causes
        })

    db.commit()
    db.refresh(db_problem)

    # Convertir JSON a string para almacenar en la BD
    db_problem.problem_tree_json = json.dumps(problem_tree)
    db.commit()


    problem_tree_dict = json.loads(db_problem.problem_tree_json)

    return {
        "id": db_problem.id,
        "central_problem": db_problem.central_problem,
        "current_description": db_problem.current_description,
        "magnitude_problem": db_problem.magnitude_problem,
        "problem_tree_json": problem_tree_dict
    }

@router.get("/", response_model=List[ProblemResponse])
def get_problems(db: Session = Depends(get_db)):
    return db.query(Problems).all()

@router.get("/{project_id}", response_model=Optional[ProblemResponse])
def get_problem(project_id: int, db: Session = Depends(get_db)):
    # Import local para evitar circular imports
    from app.models.project import Project
    
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if not project.problem:
        return JSONResponse(content={"message": "No problem created yet"}, status_code=200)

    problem = (
        db.query(Problems)
        .filter(Problems.id == project.problem.id)
        .options(
            joinedload(Problems.direct_effects).joinedload(DirectEffect.indirect_effects),
            joinedload(Problems.direct_causes).joinedload(DirectCause.indirect_causes),
        )
        .first()
    )

    if not problem:
        return JSONResponse(content={"message": "No problem created yet"}, status_code=200)

    # 🔥 Convertir `problem_tree_json` a un diccionario antes de devolverlo
    if isinstance(problem.problem_tree_json, str):
        try:
            problem.problem_tree_json = json.loads(problem.problem_tree_json)
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="Invalid JSON format in problem_tree_json")

    return problem

@router.put("/{project_id}", response_model=ProblemResponse)
def update_problem_tree(
    project_id: int,
    data: dict = Body(...),
    db: Session = Depends(get_db)
):
    from app.models.project import Project
    try:
        # Obtener el proyecto
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project.problem:
            raise HTTPException(status_code=404, detail="Problema no encontrado")

        problem = (
            db.query(Problems)
            .filter(Problems.id == project.problem.id)
            .options(
                joinedload(Problems.direct_effects).joinedload(DirectEffect.indirect_effects),
                joinedload(Problems.direct_causes).joinedload(DirectCause.indirect_causes),
            )
            .first()
        )
        if not problem:
            raise HTTPException(status_code=404, detail="Problema no encontrado")

        # Obtener el objective del proyecto
        objective = db.query(Objectives).filter(Objectives.project_id == project_id).first()

        # Actualizar el problema central
        if "central_problem" in data and data["central_problem"] != problem.central_problem:
            problem.central_problem = data["central_problem"]
            # Sincronizar con general_problem de Objectives
            if objective:
                objective.general_problem = data["central_problem"]
        
        if "current_description" in data:
            problem.current_description = data["current_description"]

        if "magnitude_problem" in data:
            problem.magnitude_problem = data["magnitude_problem"]
        
        problem.problem_tree_json = data

        # Actualizar el árbol del problema JSON
        
        # if "problem_tree_json" in data:
        #     if isinstance(data["problem_tree_json"], dict):
        #         problem.problem_tree_json = data["problem_tree_json"]
        #     else:
        #         raise HTTPException(status_code=400, detail="El campo problem_tree_json debe ser un diccionario válido.")

        # Actualizar efectos directos e indirectos
        if "direct_effects" in data:
            for effect_data in data["direct_effects"]:
                effect = db.query(DirectEffect).filter(
                    DirectEffect.id == effect_data.get("id"),
                    DirectEffect.problem_id == problem.id
                ).first() if "id" in effect_data else None

                if effect:
                    effect.description = effect_data["description"]
                else:
                    effect = DirectEffect(
                        description=effect_data["description"],
                        problem_id=problem.id
                    )
                    db.add(effect)
                    db.flush()

                # Indirect effects
                if "indirect_effects" in effect_data:
                    for indirect_data in effect_data["indirect_effects"]:
                        indirect = db.query(IndirectEffect).filter(
                            IndirectEffect.id == indirect_data.get("id"),
                            IndirectEffect.direct_effect_id == effect.id
                        ).first() if "id" in indirect_data else None

                        if indirect:
                            indirect.description = indirect_data["description"]
                        else:
                            db.add(IndirectEffect(
                                description=indirect_data["description"],
                                direct_effect_id=effect.id
                            ))

        # Actualizar causas directas e indirectas
        if "direct_causes" in data:
            # Obtener IDs de causas directas existentes para detectar eliminaciones
            existing_direct_cause_ids = {cause.id for cause in problem.direct_causes}
            updated_direct_cause_ids = set()

            for cause_data in data["direct_causes"]:
                cause = db.query(DirectCause).filter(
                    DirectCause.id == cause_data.get("id"),
                    DirectCause.problem_id == problem.id
                ).first() if "id" in cause_data else None

                old_description = None
                if cause:
                    old_description = cause.description
                    cause.description = cause_data["description"]
                    updated_direct_cause_ids.add(cause.id)
                else:
                    cause = DirectCause(
                        description=cause_data["description"],
                        problem_id=problem.id
                    )
                    db.add(cause)
                    db.flush()
                    updated_direct_cause_ids.add(cause.id)

                # Gestionar objectives_causes para causa directa
                if objective:
                    if old_description:  # Actualización
                        obj_causes = db.query(ObjectivesCauses).filter(
                            ObjectivesCauses.cause_id == cause.id,
                            ObjectivesCauses.type == "directa"
                        ).first()
                        if obj_causes:
                            obj_causes.cause_related = cause.description
                    else:  # Nueva
                        obj_causes = ObjectivesCauses(
                            type="directa",
                            cause_related=cause.description,
                            specifics_objectives=None,
                            objective_id=objective.id,
                            cause_id=cause.id
                        )
                        db.add(obj_causes)
                        db.commit()

                # Indirect causes
                if "indirect_causes" in cause_data:
                    # Obtener IDs de causas indirectas existentes para detectar eliminaciones
                    existing_indirect_cause_ids = {indirect.id for indirect in cause.indirect_causes}
                    updated_indirect_cause_ids = set()

                    for indirect_data in cause_data["indirect_causes"]:
                        indirect = db.query(IndirectCause).filter(
                            IndirectCause.id == indirect_data.get("id"),
                            IndirectCause.direct_cause_id == cause.id
                        ).first() if "id" in indirect_data else None

                        old_indirect_description = None
                        if indirect:
                            old_indirect_description = indirect.description
                            indirect.description = indirect_data["description"]
                            updated_indirect_cause_ids.add(indirect.id)
                        else:
                            indirect = IndirectCause(
                                description=indirect_data["description"],
                                direct_cause_id=cause.id
                            )
                            db.add(indirect)
                            db.flush()
                            updated_indirect_cause_ids.add(indirect.id)

                        # Gestionar objectives_causes para causa indirecta
                        if objective:
                            if old_indirect_description:  # Actualización
                                obj_causes = db.query(ObjectivesCauses).filter(
                                    ObjectivesCauses.cause_id == indirect.id,
                                    ObjectivesCauses.type == "indirecta"
                                ).first()
                                if obj_causes:
                                    obj_causes.cause_related = indirect.description
                            else:  # Nueva
                                obj_causes = ObjectivesCauses(
                                    type="indirecta",
                                    cause_related=indirect.description,
                                    specifics_objectives=None,
                                    objective_id=objective.id,
                                    cause_id=indirect.id
                                )
                                db.add(obj_causes)
                                db.commit()

                    # Eliminar causas indirectas que ya no existen
                    for indirect_id in existing_indirect_cause_ids - updated_indirect_cause_ids:
                        indirect_to_delete = db.query(IndirectCause).filter(IndirectCause.id == indirect_id).first()
                        if indirect_to_delete and objective:
                            obj_causes = db.query(ObjectivesCauses).filter(
                                ObjectivesCauses.cause_id == indirect_id,
                                ObjectivesCauses.type == "indirecta"
                            ).first()
                            if obj_causes:
                                db.delete(obj_causes)
                        db.delete(indirect_to_delete)

            # Eliminar causas directas que ya no existen
            for cause_id in existing_direct_cause_ids - updated_direct_cause_ids:
                cause_to_delete = db.query(DirectCause).filter(DirectCause.id == cause_id).first()
                if cause_to_delete and objective:
                    obj_causes = db.query(ObjectivesCauses).filter(
                        ObjectivesCauses.cause_id == cause_id,
                        ObjectivesCauses.type == "directa"
                    ).first()
                    if obj_causes:
                        db.delete(obj_causes)
                db.delete(cause_to_delete)

        db.commit()
        db.refresh(problem)

        return jsonable_encoder(problem)

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/response_ai/{project_id}")
async def post_response_ai_problem(
    project_id: int,
    message: str = Query(...),  # Se recibe como parámetro de consulta
    jsonData: dict = Body(...),  # Se recibe como JSON en el body
    db: Session = Depends(get_db)
):
    
    project = db.query(Project).filter(Project.id == project_id).first()
    problem_tree_json = project.problem.problem_tree_json
    # problem_tree_text = format_problem_tree(problem_tree_json)
    
    # ProblemTreeText = f"""
    # Árbol de Problemas:
    
    # Problema Central: {jsonData.get('central_problem', 'No especificado')}
    
    # Efectos Directos:
    # """

    # # Añadir efectos directos e indirectos
    # for effect in jsonData.get('direct_effects', []):
    #     ProblemTreeText += f"\n- {effect.get('description', '')}"
    #     if 'indirect_effects' in effect and effect['indirect_effects']:
    #         ProblemTreeText += "\n  Efectos Indirectos:"
    #         for indirect in effect['indirect_effects']:
    #             ProblemTreeText += f"\n  - {indirect.get('description', '')}"
    
    # ProblemTreeText += "\n\nCausas Directas:"
    
    # # Añadir causas directas e indirectas
    # for cause in jsonData.get('direct_causes', []):
    #     ProblemTreeText += f"\n- {cause.get('description', '')}"
    #     if 'indirect_causes' in cause and cause['indirect_causes']:
    #         ProblemTreeText += "\n  Causas Indirectas:"
    #         for indirect in cause['indirect_causes']:
    #             ProblemTreeText += f"\n  - {indirect.get('description', '')}"

    #response = await main(problem_tree_text, message)  
    #return {"response": response}
    ###Prueba de respuestas con llm
    problem = db.query(Problems).first()
    response = project.problem.chatbot.ask(message,
            info_json=str(problem_tree_json),
            project_id=project.id,
            instance=problem)
    #project.problem.chatbot.memory.clear()

    
    return response


def format_problem_tree(problem_tree_json: dict) -> str:
    formatted_text = []

    # Agregar el problema central
    formatted_text.append(f"🔹 Problema Central:\n  - {problem_tree_json['central_problem']}\n")

    # Agregar efectos directos e indirectos
    if "direct_effects" in problem_tree_json and problem_tree_json["direct_effects"]:
        formatted_text.append("🔸 Efectos Directos:")
        for effect in problem_tree_json["direct_effects"]:
            formatted_text.append(f"  - {effect['description']}")
            if "indirect_effects" in effect and effect["indirect_effects"]:
                formatted_text.append("    ➝ Efectos Indirectos:")
                for indirect in effect["indirect_effects"]:
                    formatted_text.append(f"      • {indirect['description']}")

    # Agregar causas directas e indirectas
    if "direct_causes" in problem_tree_json and problem_tree_json["direct_causes"]:
        formatted_text.append("\n🔸 Causas Directas:")
        for cause in problem_tree_json["direct_causes"]:
            formatted_text.append(f"  - {cause['description']}")
            if "indirect_causes" in cause and cause["indirect_causes"]:
                formatted_text.append("    ➝ Causas Indirectas:")
                for indirect in cause["indirect_causes"]:
                    formatted_text.append(f"      • {indirect['description']}")

    return "\n".join(formatted_text)
