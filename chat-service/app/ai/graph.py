
import hashlib
import json

from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from app.ai.state import ChatState
from app.ai.llm import llm
from app.services.document_client import search_documents
from app.redis_client import redis_client


SYSTEM_PROMPT = """
You are KnowledgeBot, an AI assistant inside a chat application.

Your responsibilities:
- Answer the user's questions clearly and accurately.
- Use previous conversation messages when they are relevant.
- Use the provided document context when answering questions about the user's documents.
- If the document context does not contain enough information, say that you do not know.
- Do not invent facts.
- Keep answers reasonably concise unless the user asks for detail.
"""


def retrieve_documents(state: ChatState):
    """
    Retrieve relevant document chunks.
    Cache the results separately for each authenticated user.
    """

    query = state["message"]
    token = state["token"]
    user_id = str(state["user_id"])
    n_results = 5

    # Create a consistent hash of the question.
    query_hash = hashlib.sha256(
        query.encode("utf-8")
    ).hexdigest()

    # Each user gets a separate cache entry.
    cache_key = (
        f"document-search:{user_id}:{query_hash}:{n_results}"
    )

    # Try Redis first.
    try:
        cached_context = redis_client.get(cache_key)

        if cached_context is not None:
            return {
                "context": json.loads(cached_context)
            }

    except Exception:
        # If Redis is unavailable, perform a normal search.
        pass

    # Cache miss: call Document Service with the JWT.
    results = search_documents(
        query=query,
        token=token,
        n_results=n_results
    )

    documents = results.get("documents", [[]])[0]
    context = "\n\n".join(documents)

    # Store the result for five minutes.
    try:
        redis_client.set(
            cache_key,
            json.dumps(context),
            ex=300
        )
    except Exception:
        # Cache failures must not break document retrieval.
        pass

    return {
        "context": context
    }


def call_llm(state: ChatState):
    """
    Send conversation history and document context to the LLM.
    """

    messages = [
        SystemMessage(content=SYSTEM_PROMPT)
    ]

    if state["context"]:
        messages.append(
            SystemMessage(
                content=f"""
Relevant document context:

{state["context"]}
"""
            )
        )

    for item in state["history"]:
        if item["role"] == "user":
            messages.append(
                HumanMessage(content=item["content"])
            )

        elif item["role"] == "assistant":
            messages.append(
                AIMessage(content=item["content"])
            )

    messages.append(
        HumanMessage(content=state["message"])
    )

    response = llm.invoke(messages)

    return {
        "response": response.content
    }


def build_chat_graph():
    graph = StateGraph(ChatState)

    graph.add_node(
        "retrieve_documents",
        retrieve_documents
    )

    graph.add_node(
        "call_llm",
        call_llm
    )

    graph.add_edge(
        START,
        "retrieve_documents"
    )

    graph.add_edge(
        "retrieve_documents",
        "call_llm"
    )

    graph.add_edge(
        "call_llm",
        END
    )

    return graph.compile()
