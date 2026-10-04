from langchain_ollama import OllamaEmbeddings

embeddings = OllamaEmbeddings(
    model="nomic-embed-text"
)

text = "FastAPI is a python framework for building APIs."

vector = embeddings.embed_query(text)

print("Embedding generated successfully.")
print("Vector length:", len(vector))
print("First 10 values:")
print(vector[:10])