import os
from langchain_ollama import OllamaEmbeddings

def create_embeddings():
    return OllamaEmbeddings(model=os.getenv("EMBED_MODEL", "nomic-embed-text"), base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"))
