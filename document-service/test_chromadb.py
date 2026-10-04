import chromadb
from langchain_ollama import OllamaEmbeddings


# 1. Create Ollama embedding model
embedding_model = OllamaEmbeddings(
    model="nomic-embed-text"
)


# 2. Create persistent ChromaDB client
client = chromadb.PersistentClient(
    path="./chroma_db"
)


# 3. Create or get collection
collection = client.get_or_create_collection(
    name="knowledge_documents"
)


# 4. Document
document = "FastAPI is a Python framework used to build APIs."


# 5. Generate embedding using Ollama
document_embedding = embedding_model.embed_query(document)


# 6. Store document + embedding in ChromaDB
collection.upsert(
    ids=["test-1"],
    documents=[document],
    embeddings=[document_embedding]
)


print("Document added to ChromaDB successfully.")


# 7. Create a search query
query = "How can I build an API using Python?"


# 8. Generate embedding for the query
query_embedding = embedding_model.embed_query(query)


# 9. Search ChromaDB
result = collection.query(
    query_embeddings=[query_embedding],
    n_results=1
)


print("\nSearch result:")
print(result)