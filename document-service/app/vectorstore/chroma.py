
import os

import chromadb
from dotenv import load_dotenv
from langchain_ollama import OllamaEmbeddings


load_dotenv()


OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://127.0.0.1:11434"
)


embedding_model = OllamaEmbeddings(
    model="nomic-embed-text",
    base_url=OLLAMA_BASE_URL
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
    """Generate an embedding and store a document chunk."""

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
    n_results: int = 5,
    document_id: int | None = None
):
    """
    Search document chunks belonging to a user.

    If document_id is supplied, search only that document.
    Duplicate text is removed while preserving search ranking.
    """

    query_embedding = embedding_model.embed_query(query)

    filters = [
        {"user_id": user_id}
    ]

    if document_id is not None:
        filters.append(
            {"document_id": document_id}
        )

    where_filter = (
        filters[0]
        if len(filters) == 1
        else {"$and": filters}
    )

    # Fetch additional candidates so duplicate text can be skipped.
    candidate_count = max(n_results * 5, 20)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=candidate_count,
        where=where_filter,
        include=["documents", "metadatas", "distances"]
    )

    ids = results.get("ids", [[]])[0]
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    unique_results = []
    seen_text = set()

    for i, content in enumerate(documents):
        normalized_text = " ".join(
            (content or "").lower().split()
        )

        if not normalized_text:
            continue

        # Skip identical text returned from duplicate chunks.
        if normalized_text in seen_text:
            continue

        seen_text.add(normalized_text)

        unique_results.append({
            "id": ids[i],
            "document": content,
            "metadata": metadatas[i] if metadatas else None,
            "distance": distances[i] if distances else None
        })

        if len(unique_results) >= n_results:
            break

    return {
        "ids": [[item["id"] for item in unique_results]],
        "documents": [
            [item["document"] for item in unique_results]
        ],
        "metadatas": [
            [item["metadata"] for item in unique_results]
        ],
        "distances": [
            [item["distance"] for item in unique_results]
        ],
        "embeddings": None
    }


def delete_document_chunks(
    document_id: int,
    user_id: int
):
    """Delete chunks belonging to one document and user."""

    collection.delete(
        where={
            "$and": [
                {"document_id": document_id},
                {"user_id": user_id}
            ]
        }
    )
