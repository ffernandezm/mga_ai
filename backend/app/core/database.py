from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Configuración de PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:ffernandez@localhost:5432/mga_db")

engine = create_engine(DATABASE_URL, echo=True)  # echo=True para ver las consultas en consola
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
