import chromadb
from langchain_ollama import OllamaEmbeddings


embedding_model = OllamaEmbeddings(
    model="nomic-embed-text"
)


client = chromadb.PersistentClient(
    path="./chroma_db"
)


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
    query_embedding = embedding_model.embed_query(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        where={
            "user_id": user_id
        }
    )

    return results


def delete_document_chunks(
    document_id: int,
    user_id: int
):
    collection.delete(
        where={
            "$and": [
                {
                    "document_id": document_id
                },
                {
                    "user_id": user_id
                }
            ]
        }
    )