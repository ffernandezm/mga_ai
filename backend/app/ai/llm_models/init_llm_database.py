import os
import psycopg
from langchain_postgres import PostgresChatMessageHistory

def init_langchain_tables():
    """
    Inicializa las tablas necesarias para LangChain en PostgreSQL.
    """
    print("🔄🔄🔄🔄🔄 Inicializando tablas de LangChain en PostgreSQL...")

    try:
        # Usa tu cadena de conexión (ajústala según tu entorno)
        conn_info = os.getenv(
            "DATABASE_URL",
            "dbname=postgres user=postgres password=ffernandez host=localhost port=5432"
        )

        # Abre la conexión
        with psycopg.connect(conn_info) as conn:
            table_name = "chat_history_"

            # Crea las tablas si no existen
            PostgresChatMessageHistory.create_tables(conn, table_name)

            print(f"✅ Tabla '{table_name}' creada o verificada correctamente.")
    except Exception as e:
        print("❌ Error al crear tablas de LangChain:", e)
