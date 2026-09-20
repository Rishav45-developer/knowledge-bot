from app.ai.llm import llm


response = llm.invoke(
    "Explain Python in one simple sentence."
)

print(response.content)