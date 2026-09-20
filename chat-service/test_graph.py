from app.ai.graph import build_chat_graph

graph = build_chat_graph()

result = graph.invoke({
    "message": "Explain what an API is in simple words.",
    "response": ""
})


print("AI RESPONSE:")
print(result["response"])