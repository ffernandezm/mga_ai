from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Configuración de PostgreSQL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:ffernandez@localhost:5432/mga_db",
)

# Algunos proveedores (Neon, Render) entregan la URL como 'postgres://'.
# SQLAlchemy 2.x requiere 'postgresql://'.
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

IS_PRODUCTION = os.getenv("ENVIRONMENT", "development").lower() == "production"

engine = create_engine(
    DATABASE_URL,
    echo=not IS_PRODUCTION,
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
