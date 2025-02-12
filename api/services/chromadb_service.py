import chromadb
from sentence_transformers import SentenceTransformer

# Inicializa o ChromaDB e a coleção de documentos
chroma_client = chromadb.PersistentClient(path="./chroma_db")  # Persiste os dados
collection = chroma_client.get_or_create_collection("knowledge_base")

# Modelo de embeddings (ajuste conforme necessário)
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

def add_document(id: str, text: str, metadata: dict = None):
    """ Adiciona um documento ao banco de vetores """
    embedding = embedding_model.encode(text).tolist()
    collection.add(ids=[id], embeddings=[embedding], metadatas=[metadata or {}], documents=[text])

def search_documents(query: str, top_k: int = 3):
    """ Busca documentos relevantes no banco de vetores """
    query_embedding = embedding_model.encode(query).tolist()
    results = collection.query(query_embeddings=[query_embedding], n_results=top_k)
    return results["documents"][0] if "documents" in results else []