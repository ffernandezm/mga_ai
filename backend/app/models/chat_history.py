# app/models/chat_history.py
"""
Chat History - Gestión de historial de conversaciones con LLM.

Almacena y recupera conversaciones entre usuarios y el asistente MGA.
"""

import uuid
import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from pydantic import BaseModel

from app.core.database import Base, SessionLocal, engine
from app.ai.llm_models.llm_manager import LLMManager
import json

# Configurar logging
logger = logging.getLogger(__name__)


# ==============================
# 🔹 MODELO ORM
# ==============================
class ChatHistory(Base):
    """Modelo de BD para historial de chat."""
    
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    tab = Column(String, nullable=False)  # problems, participants, population, etc
    session_id = Column(String, nullable=False, index=True)
    sender = Column(String, nullable=False)  # "user" o "bot"
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())


# ==============================
# 🔹 ESQUEMAS Pydantic
# ==============================
class ChatMessageBase(BaseModel):
    """Esquema base para mensajes de chat."""
    project_id: int
    tab: str
    session_id: str
    sender: str
    message: str


class ChatMessageCreate(ChatMessageBase):
    """Esquema para crear un mensaje."""
    pass


class ChatMessageResponse(ChatMessageBase):
    """Esquema para responder con un mensaje."""
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True


# ==============================
# 🔹 DEPENDENCIA DB
# ==============================
def get_db():
    """Dependencia para obtener sesión de BD."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==============================
# 🔹 FUNCIONES AUXILIARES
# ==============================
def save_chat_message(
    db: Session,
    project_id: int,
    tab: str,
    session_id: str,
    sender: str,
    message: str
) -> ChatHistory:
    """
    Guarda un mensaje en el historial de chat.
    
    Args:
        db: Sesión de BD
        project_id: ID del proyecto
        tab: Componente MGA
        session_id: ID de sesión
        sender: "user" o "bot"
        message: Contenido del mensaje
        
    Returns:
        Mensaje guardado
    """
    try:
        new_msg = ChatHistory(
            project_id=project_id,
            tab=tab,
            session_id=session_id,
            sender=sender,
            message=message,
        )
        db.add(new_msg)
        db.commit()
        db.refresh(new_msg)
        logger.info(f"✅ Mensaje guardado (id={new_msg.id}, sender={sender})")
        return new_msg
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error guardando mensaje: {str(e)}")
        raise


def get_existing_session_id(db: Session, project_id: int, tab: str) -> Optional[str]:
    """
    Busca si existe una sesión activa para un proyecto y tab.
    
    Args:
        db: Sesión de BD
        project_id: ID del proyecto
        tab: Componente MGA
        
    Returns:
        ID de sesión o None
    """
    try:
        existing = (
            db.query(ChatHistory.session_id)
            .filter(ChatHistory.project_id == project_id, ChatHistory.tab == tab)
            .order_by(ChatHistory.timestamp.desc())
            .first()
        )
        return existing[0] if existing else None
    except Exception as e:
        logger.error(f"❌ Error buscando sesión: {str(e)}")
        return None


def get_comprehensive_module_data(db: Session, project_id: int, tab: str) -> dict:
    """
    Recupera TODA la información de un módulo incluyendo sus tablas relacionadas (subtablas).
    Estructura jerárquica completa con todos los campos excepto JSON y campos internos.
    
    Args:
        db: Sesión de BD
        project_id: ID del proyecto
        tab: Nombre de la tabla/módulo principal
        
    Returns:
        Dict con estructura jerárquica de datos con formato JSON
        
    Ejemplo:
        {
            "module": "problems",
            "table": "problems",
            "total_records": 1,
            "records": [
                {
                    "central_problem": "...",
                    "current_description": "...",
                    "direct_effects": [
                        {
                            "description": "...",
                            "indirect_effects": [...]
                        }
                    ],
                    "direct_causes": [...]
                }
            ]
        }
    """
    try:
        from sqlalchemy import text, MetaData, Table, inspect, ForeignKey
        from sqlalchemy.orm import object_session
        
        # Configuración de relaciones jerárquicas (tabla padre -> [tabla hija, ...])
        relationship_map = {
            'problems': ['direct_effects', 'direct_causes'],
            'direct_effects': ['indirect_effects'],
            'direct_causes': ['indirect_causes'],
            'population': ['affected_population', 'intervention_population', 'characteristics_population'],
            'participants_general': ['participants'],
            'objectives': ['objectives_causes', 'objectives_indicators'],
            'alternatives_general': ['alternatives'],
        }
        
        # Columnas a ignorar (JSON, timestamps, IDs internos)
        ignored_columns = {
            'id', 'created_at', 'updated_at', 'deleted_at',
            'problem_tree_json', 'population_json', 'participants_json',
            'alternatives_json', '_json'
        }
        
        def serialize_value(value):
            """Convierte valores a formatos JSON-compatibles."""
            if value is None:
                return None
            if isinstance(value, (str, int, float, bool)):
                return value
            if isinstance(value, (datetime, )):
                return value.isoformat()
            return str(value)
        
        def get_record_data(table_obj, record, exclude_fk=None):
            """Extrae datos de un registro excluyendo FKs y columnas internas."""
            if exclude_fk is None:
                exclude_fk = set()
            
            data = {}
            mapper = inspect(table_obj.__class__)
            
            for column in mapper.columns:
                col_name = column.name
                
                # Saltar columnas ignoradas
                if col_name in ignored_columns:
                    continue
                if col_name in exclude_fk:
                    continue
                if col_name.endswith('_id') and col_name != 'project_id':
                    continue
                
                value = getattr(record, col_name, None)
                data[col_name] = serialize_value(value)
            
            return data
        
        def get_children_data(parent_record, parent_table, child_table_name, depth=0):
            """Recursivamente obtiene datos de tablas hijas."""
            if depth > 5:  # Límite de profundidad
                return []
            
            try:
                # Obtener relación del modelo padre
                mapper = inspect(parent_record.__class__)
                relationship_keys = [rel.key for rel in mapper.relationships]
                
                # Si el nombre exacto no está, intentar variaciones comunes
                if child_table_name not in relationship_keys:
                    # Intentar singulares/plurales
                    if child_table_name + 's' in relationship_keys:
                        child_table_name = child_table_name + 's'
                    elif child_table_name[:-1] in relationship_keys:
                        child_table_name = child_table_name[:-1]
                    else:
                        return []
                
                children = getattr(parent_record, child_table_name, None)
                if not children:
                    return []
                
                # Asegurar que es una lista
                children_list = children if isinstance(children, list) else [children]
                
                result = []
                for child in children_list:
                    if not child:
                        continue
                    
                    child_data = get_record_data(child, child)
                    
                    # Buscar relaciones dentro de este hijo
                    grandchildren_tables = relationship_map.get(child_table_name, [])
                    for grandchild_name in grandchildren_tables:
                        grandchildren = get_children_data(child, child_table_name, grandchild_name, depth + 1)
                        if grandchildren:
                            child_data[grandchild_name] = grandchildren
                    
                    result.append(child_data)
                
                return result
            except Exception as e:
                logger.warning(f"⚠️ Error obteniendo datos de {child_table_name}: {str(e)}")
                return []
        
        # PASO 1: Obtener registros de la tabla principal
        if tab not in relationship_map and tab != 'problems' and tab != 'population' and tab != 'participants_general' and tab != 'objectives' and tab != 'alternatives_general':
            # Es una tabla secundaria, obtener desde su relación
            parent_table = None
            for parent, children in relationship_map.items():
                if tab in children:
                    parent_table = parent
                    break
            
            if not parent_table:
                return {
                    "module": tab,
                    "table": tab,
                    "status": "unsupported",
                    "message": f"Tabla '{tab}' no soportada o no es una tabla principal"
                }
        
        # Importar modelos dinámicamente
        try:
            module = __import__(f'app.models.{tab}', fromlist=[tab.capitalize()])
            # Convertir snake_case a CamelCase
            class_name = ''.join(word.capitalize() for word in tab.split('_'))
            model_class = getattr(module, class_name, None)
            
            if not model_class:
                return {
                    "module": tab,
                    "table": tab,
                    "status": "error",
                    "message": f"No se pudo cargar el modelo para '{tab}'"
                }
        except ImportError as e:
            logger.error(f"❌ Error importando modelo {tab}: {str(e)}")
            return {
                "module": tab,
                "table": tab,
                "status": "error",
                "message": f"Error al importar modelo: {str(e)}"
            }
        
        # PASO 2: Consultar registros de la tabla principal
        # Cargar con relaciones anidadas para evitar lazy loading
        try:
            if tab == 'problems':
                from app.models.problems import Problems
                from app.models.direct_effects import DirectEffect
                from app.models.indirect_effects import IndirectEffect
                from app.models.direct_causes import DirectCause
                from app.models.indirect_causes import IndirectCause
                from sqlalchemy.orm import joinedload
                
                main_records = db.query(Problems).filter(
                    Problems.project_id == project_id
                ).options(
                    joinedload(Problems.direct_effects).joinedload(DirectEffect.indirect_effects),
                    joinedload(Problems.direct_causes).joinedload(DirectCause.indirect_causes)
                ).all()
            
            elif tab == 'population':
                from app.models.population import Population
                from sqlalchemy.orm import joinedload
                
                main_records = db.query(Population).filter(
                    Population.project_id == project_id
                ).options(
                    joinedload(Population.affected_population),
                    joinedload(Population.intervention_population),
                    joinedload(Population.characteristics_population)
                ).all()
            
            elif tab == 'participants_general':
                from app.models.participants_general import ParticipantsGeneral
                from sqlalchemy.orm import joinedload
                
                main_records = db.query(ParticipantsGeneral).filter(
                    ParticipantsGeneral.project_id == project_id
                ).options(
                    joinedload(ParticipantsGeneral.participants)
                ).all()
            
            elif tab == 'objectives':
                from app.models.objectives import Objectives
                from sqlalchemy.orm import joinedload
                
                main_records = db.query(Objectives).filter(
                    Objectives.project_id == project_id
                ).options(
                    joinedload(Objectives.objectives_causes),
                    joinedload(Objectives.objectives_indicators)
                ).all()
            
            elif tab == 'alternatives_general':
                from app.models.alternatives_general import AlternativesGeneral
                from sqlalchemy.orm import joinedload
                
                main_records = db.query(AlternativesGeneral).filter(
                    AlternativesGeneral.project_id == project_id
                ).options(
                    joinedload(AlternativesGeneral.alternatives)
                ).all()
            
            else:
                # Tabla genérica sin relaciones especiales
                main_records = db.query(model_class).filter(
                    model_class.project_id == project_id
                ).all()
        except Exception as e:
            logger.warning(f"⚠️ Error cargando registros con relaciones: {str(e)}, usando fallback")
            main_records = db.query(model_class).filter(
                model_class.project_id == project_id
            ).all()
        
        if not main_records:
            return {
                "module": tab,
                "table": tab,
                "total_records": 0,
                "records": []
            }
        
        # PASO 3: Construir estructura jerárquica
        records_data = []
        children_tables = relationship_map.get(tab, [])
        
        for record in main_records:
            record_data = get_record_data(record, record)
            
            # Agregar datos de tablas hijas
            for child_table in children_tables:
                try:
                    children = get_children_data(record, tab, child_table)
                    if children:
                        record_data[child_table] = children
                except Exception as e:
                    logger.warning(f"⚠️ Error procesando relación {child_table}: {str(e)}")
                    pass
            
            records_data.append(record_data)
        
        return {
            "module": tab,
            "table": tab,
            "total_records": len(main_records),
            "records": records_data
        }
    
    except Exception as e:
        logger.error(f"❌ Error recuperando datos completos de {tab}: {str(e)}")
        return {
            "module": tab,
            "table": tab,
            "status": "error",
            "message": str(e)
        }


def format_module_data_for_prompt(data: dict, max_items: int = 50) -> str:
    """
    Convierte los datos del módulo a formato natural para el prompt.
    Evita JSON técnico y presenta los datos de forma legible.
    
    Args:
        data: Dict con estructura de datos del módulo
        max_items: Máximo de items a incluir por tabla
        
    Returns:
        String con datos formateados de forma natural para el contexto
    """
    try:
        if data.get("status") == "error":
            return f"(No hay datos disponibles: {data.get('message', 'Error desconocido')})"
        
        total_records = data.get("total_records", 0)
        records = data.get("records", [])[:max_items]
        module = data.get("module", "módulo")
        
        if total_records == 0:
            return f"(No hay información registrada en {module})"
        
        # Mapeo de nombres de módulos a descripciones
        module_names = {
            "problems": "Árbol de Problemas",
            "population": "Población",
            "participants_general": "Actores del Proyecto",
            "participants": "Participantes",
            "objectives": "Objetivos",
            "alternatives_general": "Alternativas de Solución",
            "alternatives": "Alternativas Específicas",
            "direct_effects": "Efectos Directos",
            "indirect_effects": "Efectos Indirectos",
            "direct_causes": "Causas Directas",
            "indirect_causes": "Causas Indirectas",
            "affected_population": "Población Afectada",
            "intervention_population": "Población de Intervención",
            "characteristics_population": "Características de Población",
            "objectives_causes": "Causas del Objetivo",
            "objectives_indicators": "Indicadores del Objetivo"
        }
        
        module_display = module_names.get(module, module)
        
        # Construir resumen natural
        lines = []
        lines.append(f"INFORMACIÓN REGISTRADA EN {module_display.upper()}:")
        lines.append("-" * 60)
        
        def format_value(val):
            """Formatea valores de forma natural."""
            if val is None or val == "":
                return "(sin información)"
            if isinstance(val, bool):
                return "Sí" if val else "No"
            if isinstance(val, (int, float)):
                return str(val)
            return str(val)[:200]  # Truncar valores muy largos
        
        def format_record(record, indent=0):
            """Formatea un registro de forma natural."""
            prefix = "  " * indent
            parts = []
            
            for key, value in record.items():
                # Saltar listas (subtablas) - se manejan de forma especial
                if isinstance(value, list):
                    if value:  # Solo mostrar si tiene contenido
                        total_count = len(value)
                        label = f"{key.replace('_', ' ').title()}: {total_count} registro{'s' if total_count > 1 else ''}"
                        parts.append(f"{prefix}• {label}")
                else:
                    # Mostrar valores simples
                    clean_key = key.replace('_', ' ').title()
                    clean_val = format_value(value)
                    if clean_val != "(sin información)":
                        parts.append(f"{prefix}• {clean_key}: {clean_val}")
            
            return "\n".join(parts) if parts else f"{prefix}(sin información completa)"
        
        # Agregar registros formateados
        for idx, record in enumerate(records, 1):
            if len(records) > 1:
                lines.append(f"\nRegistro {idx}:")
            lines.append(format_record(record))
        
        lines.append("-" * 60)
        
        # Agregar nota sobre cantidad de registros
        if total_records > max_items:
            lines.append(f"(Mostrando {len(records)} de {total_records} registro{'s' if total_records > 1 else ''})")
        
        return "\n".join(lines)
        
    except Exception as e:
        logger.error(f"❌ Error formateando datos: {str(e)}")
        return f"(Error al procesar los datos del módulo: {str(e)[:50]})"



def get_module_data(db: Session, project_id: int, tab: str) -> str:
    """
    Recupera TODOS los datos registrados en cualquier tabla/módulo del proyecto.
    Funciona dinámicamente sin hardcodear campos específicos.
    
    Args:
        db: Sesión de BD
        project_id: ID del proyecto
        tab: Nombre de la tabla/módulo
        
    Returns:
        String formateado con toda la información disponible
    """
    try:
        context_lines = []
        context_lines.append("\n" + "="*70)
        context_lines.append(f"INFORMACIÓN REGISTRADA EN {tab.upper()}:")
        context_lines.append("="*70)
        
        from sqlalchemy import text, inspect, MetaData, Table
        
        # 1. Obtener información de la tabla
        metadata = MetaData()
        metadata.reflect(bind=db.bind)
        
        if tab not in metadata.tables:
            context_lines.append(f"(Tabla '{tab}' no encontrada)")
            context_lines.append("="*70)
            return "\n".join(context_lines)
        
        table = metadata.tables[tab]
        columns = [col.name for col in table.columns]
        
        # 2. Determinar cómo filtrar por proyecto
        # Algunas tablas tienen project_id directo, otras vía relación
        
        has_project_id = 'project_id' in columns
        
        if has_project_id:
            # Tabla con project_id directo
            query = f"SELECT * FROM {tab} WHERE project_id = :project_id"
            params = {"project_id": project_id}
        else:
            # Intentar encontrar relación a través de otra tabla
            # Mapeo de relaciones comunes
            relation_map = {
                'participants': 'participants_general',
                'objectives_causes': 'objectives',
                'objectives_indicators': 'objectives',
                'direct_causes': 'problems',
                'direct_effects': 'problems',
                'indirect_causes': 'problems',
                'indirect_effects': 'problems',
                'affected_population': 'population',
                'intervention_population': 'population',
                'characteristics_population': 'population',
                'alternatives': 'alternatives_general',
            }
            
            parent_table = relation_map.get(tab)
            
            if parent_table and parent_table in metadata.tables:
                # Obtener columna de FK a tabla padre
                parent_col = f"{parent_table}_id"
                if parent_col in columns:
                    # Query con JOIN
                    query = f"""
                        SELECT {tab}.* FROM {tab}
                        INNER JOIN {parent_table} ON {tab}.{parent_col} = {parent_table}.id
                        WHERE {parent_table}.project_id = :project_id
                    """
                else:
                    query = None
            else:
                query = None
            
            params = {"project_id": project_id}
        
        if not query:
            # Último intento: buscar FK que apunte a project_id
            query_result = db.execute(
                text(f"""
                    SELECT column_name FROM information_schema.columns
                    WHERE table_name = :table AND column_name LIKE '%project_id%'
                """),
                {"table": tab}
            ).fetchone()
            
            if query_result:
                query = f"SELECT * FROM {tab} WHERE {query_result[0]} = :project_id"
            else:
                context_lines.append(f"(No hay relación con proyecto para tabla '{tab}')")
                context_lines.append("="*70)
                return "\n".join(context_lines)
        
        # 3. Ejecutar query y recuperar datos
        result = db.execute(text(query), params).fetchall()
        
        if not result:
            context_lines.append(f"(No hay registros en {tab} para este proyecto)")
        else:
            context_lines.append(f"\nTotal de registros: {len(result)}\n")
            
            # Mostrar cada registro
            for idx, row in enumerate(result, 1):
                context_lines.append(f"Registro {idx}:")
                # Iterar sobre cada columna
                for col_idx, col_name in enumerate(columns):
                    value = row[col_idx] if col_idx < len(row) else None
                    
                    # Saltar columnas internas (IDs de relaciones, timestamps de auditoría)
                    if col_name.endswith('_id') and col_name not in ['project_id']:
                        continue
                    if col_name in ['created_at', 'updated_at', 'id']:
                        continue
                    
                    # Formatear valor
                    if value is None:
                        value_str = "(vacío)"
                    elif isinstance(value, bool):
                        value_str = "Sí" if value else "No"
                    elif isinstance(value, str) and len(value) > 100:
                        value_str = value[:100] + "..."
                    else:
                        value_str = str(value)
                    
                    # Nombre de columna en formato legible
                    readable_name = col_name.replace('_', ' ').title()
                    context_lines.append(f"  • {readable_name}: {value_str}")
                
                context_lines.append("")  # Línea en blanco entre registros
        
        context_lines.append("="*70)
        
        context = "\n".join(context_lines)
        logger.info(f"📊 Contexto del módulo {tab} recuperado ({len(context)} chars, {len(result) if result else 0} registros)")
        return context
        
    except Exception as e:
        logger.warning(f"⚠️ Error recuperando datos del módulo {tab}: {str(e)}")
        return ""


# ==============================
# 🔹 ROUTER FastAPI
# ==============================
router = APIRouter(prefix="/chat_history", tags=["chat"])
llm_manager = LLMManager()


@router.post("/chat/{project_id}/{tab}", response_model=ChatMessageResponse)
def chat_with_ai(
    project_id: int,
    tab: str,
    question: str = Body(..., embed=True),
    db: Session = Depends(get_db),
):
    """
    Envía un mensaje al chatbot y guarda tanto la pregunta como la respuesta.
    El LLM recibe el historial completo de la conversación para mayor contexto.
    
    Args:
        project_id: ID del proyecto
        tab: Componente MGA (problems, participants, population, objectives, alternatives)
        question: Pregunta del usuario
        db: Sesión de BD
        
    Returns:
        Respuesta del bot con metadatos
    """
    try:
        logger.info(f"📨 Chat recibido: project={project_id}, tab={tab}")
        
        # 🆕 Validar tab dinámicamente contra tablas disponibles en BD
        from sqlalchemy import MetaData
        
        metadata = MetaData()
        metadata.reflect(bind=db.bind)
        available_tables = list(metadata.tables.keys())
        
        # Tablas que no son módulos MGA (excluir del chat)
        excluded_tables = ['projects', 'chat_history', 'survey', 'alembic_version']
        valid_tabs = [t for t in available_tables if t not in excluded_tables]
        
        if tab not in valid_tabs:
            logger.warning(f"⚠️ Tab no válido: {tab}. Opciones: {', '.join(valid_tabs)}")
            raise HTTPException(
                status_code=400,
                detail=f"Tab '{tab}' no válido. Opciones disponibles: {', '.join(valid_tabs)}"
            )
        
        # Obtener o crear sesión
        session_id = get_existing_session_id(db, project_id, tab) or str(uuid.uuid4())
        logger.info(f"🔗 Session ID: {session_id[:8]}...")

        # Guardar pregunta del usuario
        user_message = save_chat_message(db, project_id, tab, session_id, "user", question)

        # 🆕 Recuperar historial de chat anterior para contexto
        logger.info(f"📜 Recuperando historial de chat para contexto...")
        previous_messages = (
            db.query(ChatHistory)
            .filter(
                ChatHistory.project_id == project_id,
                ChatHistory.tab == tab,
                ChatHistory.session_id == session_id
            )
            .order_by(ChatHistory.timestamp.asc())
            .all()
        )
        
        # Convertir mensajes ORM a diccionarios para el LLM
        chat_history = [
            {
                "sender": msg.sender,
                "message": msg.message,
                "timestamp": msg.timestamp
            }
            for msg in previous_messages[:-1]  # Excluir el mensaje del usuario que acabamos de guardar
        ]
        
        logger.info(f"📚 Historial de {len(chat_history)} mensajes anteriores recuperado")

        # 🆕 MEJORADO: Recuperar datos COMPLETOS del módulo con estructura jerárquica
        logger.info(f"📊 Recuperando datos COMPLETOS del módulo {tab} (incluyendo subtablas)...")
        comprehensive_data = get_comprehensive_module_data(db, project_id, tab)
        
        # Formatear datos para el prompt
        module_context = format_module_data_for_prompt(comprehensive_data, max_items=50)
        
        logger.info(f"✅ Contexto del módulo {tab} recuperado ({comprehensive_data.get('total_records', 0)} registros en BD)")

        # Llamar modelo LLM con historial Y datos COMPLETOS del módulo
        logger.info(f"🤖 Invocando LLM para tab={tab} con contexto completo de chat y módulo")
        answer = llm_manager.ask(
            question=question,
            tab=tab,
            context=module_context,  # 🆕 Datos COMPLETOS con estructura jerárquica
            chat_history=chat_history if chat_history else None,  # Pasar historial si existe
            session_id=session_id
        )

        # Guardar respuesta del bot
        bot_message = save_chat_message(db, project_id, tab, session_id, "bot", answer)
        logger.info(f"✅ Respuesta guardada (id={bot_message.id}, con historial de {len(chat_history)} msgs)")

        return bot_message
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error en chat_with_ai: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=f"Error en el chat: {str(e)}"
        )


@router.get("/{project_id}/{tab}", response_model=List[ChatMessageResponse])
def get_chat_history(
    project_id: int,
    tab: str,
    db: Session = Depends(get_db)
):
    """
    Devuelve el historial de chat de un proyecto y componente.
    
    Args:
        project_id: ID del proyecto
        tab: Componente MGA
        db: Sesión de BD
        
    Returns:
        Lista de mensajes ordenados cronológicamente
    """
    try:
        logger.info(f"📋 Obteniendo historial: project={project_id}, tab={tab}")
        
        messages = (
            db.query(ChatHistory)
            .filter(
                ChatHistory.project_id == project_id,
                ChatHistory.tab == tab
            )
            .order_by(ChatHistory.timestamp.asc())
            .all()
        )
        
        logger.info(f"✅ Se recuperaron {len(messages)} mensajes")
        return messages
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo historial: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener historial: {str(e)}"
        )


@router.delete("/{project_id}/{tab}")
def clear_chat_history(
    project_id: int,
    tab: str,
    db: Session = Depends(get_db)
):
    """
    Elimina todos los mensajes del historial de chat.
    
    Args:
        project_id: ID del proyecto
        tab: Componente MGA
        db: Sesión de BD
        
    Returns:
        Confirmación de mensajes eliminados
    """
    try:
        logger.info(f"🗑️ Limpiando chat: project={project_id}, tab={tab}")
        
        deleted = (
            db.query(ChatHistory)
            .filter(
                ChatHistory.project_id == project_id,
                ChatHistory.tab == tab
            )
            .delete()
        )
        db.commit()
        
        if deleted == 0:
            logger.warning(f"⚠️ No hay mensajes para eliminar")
            raise HTTPException(
                status_code=404,
                detail="No se encontraron mensajes para eliminar"
            )
        
        logger.info(f"✅ Se eliminaron {deleted} mensajes")
        return {
            "message": f"Se eliminaron {deleted} mensajes del chat",
            "deleted_count": deleted
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error limpiando chat: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al limpiar chat: {str(e)}"
        )