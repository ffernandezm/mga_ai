from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

def get_database_url() -> str:
    """Construye una URL PostgreSQL escapando credenciales de forma segura."""
    explicit_url = os.getenv("DATABASE_URL", "").strip()
    if explicit_url:
        if explicit_url.startswith("postgres://"):
            return explicit_url.replace("postgres://", "postgresql://", 1)
        return explicit_url

    password = os.getenv("POSTGRES_PASSWORD")
    if password is not None:
        return URL.create(
            drivername="postgresql",
            username=os.getenv("POSTGRES_USER", "mga"),
            password=password,
            host=os.getenv("POSTGRES_HOST", "db"),
            port=int(os.getenv("POSTGRES_PORT", "5432")),
            database=os.getenv("POSTGRES_DB", "mga"),
        ).render_as_string(hide_password=False)

    return "postgresql:///mga_db"


DATABASE_URL = get_database_url()

# Algunos proveedores (Neon, Render) entregan la URL como 'postgres://'.
# SQLAlchemy 2.x requiere 'postgresql://'.
IS_PRODUCTION = os.getenv("ENVIRONMENT", "development").lower() == "production"

engine = create_engine(
    DATABASE_URL,
    echo=not IS_PRODUCTION,
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
