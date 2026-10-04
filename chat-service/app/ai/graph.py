from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from app.ai.state import ChatState
from app.ai.llm import llm


SYSTEM_PROMPT = """
You are KnowledgeBot, an AI assistant inside a chat application.

Your responsibilities:
- Answer the user's questions clearly and accurately.
- Use previous conversation messages when they are relevant.
- If you do not know something, say that you do not know.
- Do not invent facts.
- Keep answers reasonably concise unless the user asks for detail.
"""


def call_llm(state: ChatState):

    messages = []

    # System instructions
    messages.append(
        SystemMessage(content=SYSTEM_PROMPT)
    )

    # Previous conversation history
    for item in state["history"]:

        if item["role"] == "user":
            messages.append(
                HumanMessage(content=item["content"])
            )

        elif item["role"] == "assistant":
            messages.append(
                AIMessage(content=item["content"])
            )

    # Current user message
    messages.append(
        HumanMessage(content=state["message"])
    )

    # Send complete conversation to LLM
    response = llm.invoke(messages)

    return {
        "response": response.content
    }


def build_chat_graph():

    graph = StateGraph(ChatState)

    graph.add_node("call_llm", call_llm)

    graph.add_edge(START, "call_llm")

    graph.add_edge("call_llm", END)

    return graph.compile()