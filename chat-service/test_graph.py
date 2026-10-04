from app.ai.graph import build_chat_graph


graph = build_chat_graph()


result = graph.invoke({
    "message": "Who created it?",
    "history": [
        {
            "role": "user",
            "content": "What is Python?"
        },
        {
            "role": "assistant",
            "content": "Python is a programming language."
        }
    ],
    "response": ""
})


print("AI RESPONSE:")
print(result["response"])