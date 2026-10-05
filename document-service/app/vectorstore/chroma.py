import chromadb
from langchain_ollama import OllamaEmbeddings


# Ollama embedding model
embedding_model = OllamaEmbeddings(
    model="nomic-embed-text"
)


# Persistent ChromaDB client
client = chromadb.PersistentClient(
    path="./chroma_db"
)


# Collection for document chunks
collection = client.get_or_create_collection(
    name="knowledge_documents"
)


def store_chunk(
    chunk_id: str,
    content: str,
    document_id: int,
    chunk_index: int,
    user_id: int,
    filename: str
):
    """
    Generate an embedding for a document chunk
    and store it in ChromaDB.
    """

    embedding = embedding_model.embed_query(content)

    collection.upsert(
        ids=[chunk_id],
        documents=[content],
        embeddings=[embedding],
        metadatas=[
            {
                "document_id": document_id,
                "chunk_index": chunk_index,
                "user_id": user_id,
                "filename": filename
            }
        ]
    )


def search_chunks(
    query: str,
    user_id: int,
    n_results: int = 5
):
    """
    Search ChromaDB for document chunks
    relevant to the user's query.
    """

    query_embedding = embedding_model.embed_query(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        where={
            "user_id": user_id
        }
    )

    return results