import os

from langchain_ollama import ChatOllama
from dotenv import load_dotenv

load_dotenv()

OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://127.0.0.1:11434"
)

llm = ChatOllama(
    model="qwen2.5-coder:3b",
    temperature=0,
    base_url=OLLAMA_BASE_URL
)