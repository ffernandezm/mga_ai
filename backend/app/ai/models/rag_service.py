"""
Servicio de RAG (Retrieval-Augmented Generation) para el documento conceptual MGA.

Extrae contexto relevante del documento usando embeddings y búsqueda semántica FAISS.
Permite enriquecer los prompts de LLM con información del documento.
"""

import logging
import os
from typing import List, Dict, Optional

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

# Configurar logging
logger = logging.getLogger(__name__)


class DocumentRAG:
    """
    Servicio de RAG para documentos MGA.
    
    Proporciona búsqueda semántica en documentos PDF usando embeddings y FAISS.
    Recupera fragmentos de texto relevantes según consultas de usuario.
    """
    
    # Configuración de modelo de embeddings
    DEFAULT_EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    DEFAULT_CHUNK_SIZE = 1000
    DEFAULT_CHUNK_OVERLAP = 200
    
    def __init__(
        self,
        pdf_path: Optional[str] = None,
        embed_model: str = DEFAULT_EMBED_MODEL
    ):
        """
        Inicializa el servicio de RAG.
        
        Args:
            pdf_path: Ruta al documento PDF. Si es None, se usa PDF_PATH del .env
            embed_model: Modelo de embeddings a usar (default: all-MiniLM-L6-v2)
        """
        if pdf_path is None:
            pdf_path = os.getenv(
                "PDF_PATH",
                "/home/ffernandez/mga_ai/backend/app/data/Documento_conceptual_2023.pdf"
            )
        
        self.pdf_path = pdf_path
        self.embed_model_name = embed_model
        self.vectorstore: Optional[FAISS] = None
        self.documents: List[Document] = []
        self.embeddings: Optional[HuggingFaceEmbeddings] = None
        
        # Intentar cargar o crear el vectorstore
        self._initialize_vectorstore()
    
    def _initialize_vectorstore(self) -> None:
        """
        Inicializa o carga el vectorstore FAISS.
        
        Si el documento PDF existe, lo carga y crea embeddings.
        Si no existe, crea un vectorstore con contexto genérico de MGA.
        """
        try:
            logger.info(f"📄 Inicializando RAG con documento: {self.pdf_path}")
            
            # Cargar embeddings
            logger.info(f"🔄 Cargando modelo de embeddings: {self.embed_model_name}")
            self.embeddings = HuggingFaceEmbeddings(model_name=self.embed_model_name)
            logger.info("✅ Modelo de embeddings cargado")
            
            # Intentar cargar documento PDF
            if os.path.exists(self.pdf_path):
                logger.info(f"📖 Cargando PDF desde: {self.pdf_path}")
                loader = PyPDFLoader(self.pdf_path)
                pages = loader.load()
                logger.info(f"✅ PDF cargado: {len(pages)} páginas")
                
                # Dividir el documento en chunks
                logger.info(f"✂️ Dividiendo documento en chunks (tamaño={self.DEFAULT_CHUNK_SIZE})...")
                splitter = RecursiveCharacterTextSplitter(
                    chunk_size=self.DEFAULT_CHUNK_SIZE,
                    chunk_overlap=self.DEFAULT_CHUNK_OVERLAP,
                    separators=["\n\n", "\n", ". ", " ", ""]
                )
                self.documents = splitter.split_documents(pages)
                logger.info(f"✅ Documento dividido en {len(self.documents)} chunks")
                
                # Crear vectorstore
                logger.info("🔍 Creando índice FAISS...")
                self.vectorstore = FAISS.from_documents(
                    self.documents,
                    self.embeddings
                )
                logger.info(f"✅ RAG inicializado con {len(self.documents)} chunks del documento")
            else:
                logger.warning(f"⚠️ Documento no encontrado en {self.pdf_path}")
                logger.info("   → Se usarán contextos genéricos de MGA")
                self._create_default_context()
                
        except Exception as e:
            logger.error(f"❌ Error inicializando RAG: {e}", exc_info=True)
            logger.info("   → Se usarán contextos genéricos de MGA")
            self._create_default_context()
    
    def _create_default_context(self) -> None:
        """Crea contexto por defecto si el documento no está disponible"""
        default_context = """
METODOLOGÍA GENERAL AJUSTADA (MGA) - COLOMBIA

La MGA es una metodología utilizada en Colombia para formular proyectos de inversión pública.

COMPONENTES PRINCIPALES:
1. Árbol de Problemas: Diagnóstico de la situación negativa
2. Análisis de Participantes: Identificación de actores clave
3. Análisis de Población: Caracterización de beneficiarios
4. Árbol de Objetivos: Lo que se espera lograr
5. Análisis de Alternativas: Opciones de solución
        """
        
        self.documents = [
            Document(page_content=default_context, metadata={"source": "default"})
        ]
        
        if self.embeddings:
            try:
                self.vectorstore = FAISS.from_documents(
                    self.documents,
                    self.embeddings
                )
                logger.info("✅ Vectorstore por defecto creado")
            except Exception as e:
                logger.warning(f"⚠️ Error creando vectorstore por defecto: {e}")
    
    def retrieve_context(self, query: str, k: int = 3, component: str = None) -> str:
        """
        Recupera contexto relevante basado en una query.
        
        Args:
            query: Consulta para buscar en el documento
            k: Número de resultados a retornar
            component: Componente específico (problems, participants, etc.)
        
        Returns:
            str: Contexto relevante como string
        """
        if not self.vectorstore:
            return self._get_default_component_context(component)
        
        try:
            # Buscar documentos similares
            results = self.vectorstore.similarity_search(query, k=k)
            
            # Combinar resultados
            context = "\n\n".join([
                f"[{doc.metadata.get('source', 'documento')}]\n{doc.page_content}"
                for doc in results
            ])
            
            return context if context.strip() else self._get_default_component_context(component)
            
        except Exception as e:
            logger.warning(f"⚠️ Error en búsqueda RAG: {e}")
            return self._get_default_component_context(component)
    
    def _get_default_component_context(self, component: Optional[str]) -> str:
        """Retorna contexto genérico por componente"""
        contexts = {
            "problems": """
ÁRBOL DE PROBLEMAS
El árbol de problemas es una técnica para identificar y visualizar las causas 
y efectos de un problema central. Se estructura en:
- Problema Central: La situación negativa identificada
- Causas (raíces): ¿Por qué existe el problema?
- Efectos (ramas): ¿Qué consecuencias genera?
            """,
            
            "participants": """
PARTICIPANTES Y ACTORES
Identifica a todos los actores involucrados:
- Actores directos: Beneficiarios y ejecutores
- Actores indirectos: Instituciones relacionadas
- Actores afectados: Otros impactados
- Análisis de intereses: Qué quieren conseguir
            """,
            
            "population": """
POBLACIÓN Y BENEFICIARIOS
Caracteriza la población que se beneficiará:
- Población total: Cantidad de habitantes
- Población objetivo: Directamente beneficiada
- Características demográficas: Edad, género, ubicación
- Condiciones socioeconómicas: Ingresos, educación
            """,

            "requirements_general": """
REQUERIMIENTOS GENERALES
Define los requerimientos clave para la intervención:
- Bienes y servicios necesarios para la ejecución
- Estimación inicial de cantidades y estándares de calidad
- Relación oferta-demanda de los recursos requeridos
- Priorización técnica según impacto y factibilidad
            """,
            
            "objectives": """
OBJETIVOS DEL PROYECTO
Especifica lo que se quiere lograr:
- Objetivo general: Cambio transformacional
- Objetivos específicos: Logros concretos y medibles
- Indicadores: Cómo se medirá el logro
- Metas: Valores esperados por período
            """,

            "value_chain": """
CADENA DE VALOR
Estructura la lógica operativa del proyecto:
- Eslabones o etapas de transformación
- Actividades e insumos necesarios por etapa
- Productos o resultados intermedios y finales
- Riesgos y cuellos de botella que afectan la ejecución
            """,
            
            "alternatives": """
ALTERNATIVAS DE SOLUCIÓN
Plantea diferentes formas de resolver el problema:
- Alternativa 1: Primera opción con costos y beneficios
- Alternativa 2: Segunda opción
- Análisis comparativo: Pros y contras
- Selección: Alternativa recomendada con justificación
            """
        }
        
        return contexts.get(component, contexts["problems"])


# Instancia global del servicio RAG
_rag_service: Optional[DocumentRAG] = None


def get_rag_service() -> DocumentRAG:
    """
    Obtiene la instancia global del servicio RAG (lazy initialization).
    
    Returns:
        DocumentRAG: Instancia del servicio RAG
    """
    global _rag_service
    if _rag_service is None:
        _rag_service = DocumentRAG()
    return _rag_service
