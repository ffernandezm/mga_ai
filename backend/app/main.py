"""
FastAPI Application - MGA Backend.

Servidor FastAPI para gestión de proyectos de inversión pública
usando la Metodología General Ajustada (MGA) con integración de LLM.
"""

import logging
import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

# Configurar logging
load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Importar routers
from app.models.project import router as project_router
from app.models.problems import router as problem_router
from app.models.direct_effects import router as direct_effect_router
from app.models.indirect_effects import router as indirect_effect_router
from app.models.direct_causes import router as direct_cause_router
from app.models.indirect_causes import router as indirect_cause_router
from app.models.participants import router as participants_router
from app.models.participants_general import router as participants_general_router
from app.models.objectives import router as objectives_router
from app.models.objectives_indicators import router as objectives_indicator_router
from app.models.objectives_causes import router as objectives_causes_router
from app.models.alternatives_general import router as alternatives_general_router
from app.models.alternatives import router as alternatives_router
from app.models.population import router as population_router
from app.models.affected_population import router as affected_population_router
from app.models.intervention_population import router as intervention_population_router
from app.models.characteristics_population import router as characteristics_population_router
from app.models.requirements import router as requirements_router
from app.models.requirements_general import router as requirements_general_router
from app.models.technical_analysis import router as technical_analysis_router
from app.models.localization_general import router as localization_general_router
from app.models.localization import router as localization_router
from app.models.survey import router as survey_router
from app.models.chat_history import router as chat_history_router
from app.models.get_table_data import router as get_table_data_router
from app.models.value_chain import router as value_chain_router
from app.models.value_chain_objectives import router as value_chain_objectives_router
from app.models.product import router as product_router
from app.models.activity import router as activity_router
from app.models.development_plans import router as development_plan_router
from app.models.pnd import router as pnd_router
from app.models.product_catalog import router as product_catalog_router
from app.models.project_localization import router as project_localization_router

from app.core.database import Base, engine
from app.ai.llm_models.init_llm_database import init_langchain_tables


# ==============================
# 🔹 LIFESPAN CONTEXT MANAGER
# ==============================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestiona el ciclo de vida de la aplicación."""
    # Startup
    logger.info("🚀 Iniciando MGA Backend...")
    try:
        # Crear tablas
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Tablas de BD creadas/verificadas")
        
        # Inicializar tablas de LangChain
        init_langchain_tables()
        logger.info("✅ Tablas de LangChain inicializadas")
        
        # Cargar catálogo de productos desde CSV
        from app.models.product_catalog import seed_product_catalogs
        seed_product_catalogs()
        logger.info("✅ Catálogo de productos cargado/verificado")
        
        # Validar LLM
        llm_provider = os.getenv("LLM_PROVIDER", "groq").lower()
        logger.info(f"✅ LLM Provider configurado: {llm_provider}")
        
    except Exception as e:
        logger.error(f"❌ Error en startup: {str(e)}", exc_info=True)
        raise
    
    yield
    
    # Shutdown
    logger.info("👋 Apagando MGA Backend...")


# ==============================
# 🔹 CREAR APLICACIÓN FASTAPI
# ==============================
app = FastAPI(
    title="MGA Backend API",
    description="API para gestión de proyectos MGA con LLM integrado",
    version="1.0.0",
    lifespan=lifespan
)


# ==============================
# 🔹 CONFIGURAR CORS
# ==============================
origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]

env = os.getenv("ENVIRONMENT", "development").lower()
if env == "production":
    # En producción, ser más restrictivo
    origins = [
        os.getenv("FRONTEND_URL", "https://yourdomain.com"),
    ]
else:
    # En desarrollo, permitir todos los orígenes
    origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger.info(f"✅ CORS configurado para: {origins}")


# ==============================
# 🔹 EXCEPTION HANDLERS
# ==============================
@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    """Handler para errores de validación."""
    logger.warning(f"⚠️ Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "message": "Error de validación"
        }
    )


# ==============================
# 🔹 ENDPOINTS GENERALES
# ==============================
@app.get("/")
async def read_root():
    """Health check básico."""
    return {
        "message": "MGA Backend API",
        "status": "operational",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Endpoint de salud detallado."""
    return {
        "status": "healthy",
        "service": "MGA Project Assistant API",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "llm_provider": os.getenv("LLM_PROVIDER", "groq")
    }


# ==============================
# 🔹 REGISTRAR ROUTERS
# ==============================
logger.info("📝 Registrando routers...")

# Routers de proyectos y modelos
app.include_router(project_router, prefix="/projects", tags=["Projects"])
app.include_router(problem_router, prefix="/problems", tags=["Problems"])
app.include_router(direct_effect_router, prefix="/direct_effects", tags=["DirectEffects"])
app.include_router(indirect_effect_router, prefix="/indirect_effects", tags=["IndirectEffects"])
app.include_router(direct_cause_router, prefix="/direct_causes", tags=["DirectCauses"])
app.include_router(indirect_cause_router, prefix="/indirect_causes", tags=["IndirectCauses"])
app.include_router(participants_general_router, prefix="/participants_general", tags=["ParticipantsGeneral"])
app.include_router(participants_router, prefix="/participants", tags=["Participants"])
app.include_router(objectives_router, prefix="/objectives", tags=["Objectives"])
app.include_router(objectives_indicator_router, prefix="/objectives_indicator", tags=["ObjectivesIndicator"])
app.include_router(objectives_causes_router, prefix="/objectives_causes", tags=["ObjectivesCauses"])
app.include_router(alternatives_general_router, prefix="/alternatives_general", tags=["AlternativesGeneral"])
app.include_router(alternatives_router, prefix="/alternatives", tags=["Alternatives"])
app.include_router(population_router, prefix="/population", tags=["Population"])
app.include_router(affected_population_router, prefix="/affected_population", tags=["AffectedPopulation"])
app.include_router(intervention_population_router, prefix="/intervention_population", tags=["InterventionPopulation"])
app.include_router(requirements_router, prefix="/requirements", tags=["Requirements"])
app.include_router(requirements_general_router, prefix="/requirements_general", tags=["RequirementsGeneral"])
app.include_router(characteristics_population_router, prefix="/characteristics_population", tags=["CharacteristicsPopulation"])
app.include_router(technical_analysis_router, prefix="/technical_analysis", tags=["TechnicalAnalysis"])
app.include_router(localization_general_router, prefix="/localization_general", tags=["LocalizationGeneral"])
app.include_router(localization_router, prefix="/localization", tags=["Localization"])

app.include_router(survey_router, prefix="/survey", tags=["Survey"])

app.include_router(value_chain_router, prefix="/value_chains", tags=["ValueChains"])
app.include_router(value_chain_objectives_router, prefix="/value_chain_objectives", tags=["ValueChainObjectives"])
app.include_router(product_router, prefix="/products", tags=["Products"])
app.include_router(activity_router, prefix="/activities", tags=["Activities"])
app.include_router(development_plan_router, prefix="/development_plans", tags=["DevelopmentPlans"])
app.include_router(pnd_router, prefix="/pnd", tags=["PND"])
app.include_router(product_catalog_router, prefix="/product_catalogs", tags=["ProductCatalogs"])
app.include_router(project_localization_router, prefix="/project_localizations", tags=["ProjectLocalizations"])

# Router de chat (ya tiene su prefijo incluido en el router)
app.include_router(chat_history_router, tags=["ChatHistory"])

# Router de datos
app.include_router(get_table_data_router, prefix="/api", tags=["Data"])

logger.info("Todos los routers registrados")