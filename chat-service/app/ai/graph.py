from langgraph.graph import StateGraph, START, END

from app.ai.state import ChatState
from app.ai.llm import llm

def call_llm(state: ChatState):
    response = llm.invoke(state["message"])

    return {
        "response": response.content
    }

def build_chat_graph():

    graph = StateGraph(ChatState)

    graph.add_node("call_llm", call_llm)

    graph.add_edge(START, "call_llm")
    graph.add_edge("call_llm", END)

    return graph.compile()





