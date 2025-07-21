from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.models.project import router as project_router
from app.models.problem import router as problem_router
from app.models.participants import router as participants_router
from app.models.participants_general import router as participants_general_router
from app.models.objectives import router as objectives_router
from app.models.alternatives import router as alternatives_router
from app.models.population import router as population_router
from app.core.database import Base, engine

import asyncio

try:
    asyncio.get_running_loop()
except RuntimeError:
    asyncio.run(asyncio.sleep(0))

app = FastAPI(title="FastAPI Project with PostgreSQL")

# Habilitar CORS para permitir peticiones desde el frontend

origins = [
    "http://localhost:5173",  # origen del frontend
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,             # permitir orígenes
    allow_credentials=True,
    allow_methods=["*"],               # permitir todos los métodos (GET, POST, etc.)
    allow_headers=["*"],               # permitir todos los headers
)

# Crear tablas en la base de datos
Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"message": "FastAPI está funcionando correctamente 🚀"}

# Incluir Rutas
app.include_router(project_router, prefix="/projects", tags=["Projects"])
app.include_router(problem_router, prefix="/problems", tags=["Problems"])
app.include_router(participants_general_router, prefix="/participants_general", tags=["ParticipantsGeneral"])
app.include_router(participants_router, prefix="/participants", tags=["Participants"])
app.include_router(objectives_router, prefix="/objectives", tags=["Objectives"])
app.include_router(alternatives_router, prefix="/alternatives", tags=["Alternatives"])
app.include_router(population_router, prefix="/population", tags=["Population"])
