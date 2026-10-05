from app.vectorstore.chroma import search_chunks


results = search_chunks(
    query="What is FastAPI?",
    user_id=4,
    n_results=5
)

print("Search results:")
print(results)