from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from config.config import OPENAI_API_KEY

class EmbeddingModel:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
        self.vector_store = None

    def process_text(self, text):
        """Divide el texto en fragmentos y genera embeddings."""
        text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        text_chunks = text_splitter.split_text(text)
        self.vector_store = FAISS.from_texts(text_chunks, self.embeddings)

    def search_similar(self, query, k=3):
        """Realiza búsqueda en los embeddings."""
        if self.vector_store:
            docs = self.vector_store.similarity_search(query, k=k)
            return "\n".join([doc.page_content for doc in docs])
        return ""
