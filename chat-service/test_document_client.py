from app.services.document_client import search_documents

TOKEN = "Your_jwt_token"

results = search_documents(
    query="What is this document about?",
    token=TOKEN,
    n_results=5
)

print("Document search results:")
print(results)