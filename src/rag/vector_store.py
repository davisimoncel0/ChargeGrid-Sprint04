from pathlib import Path
from langchain_chroma import Chroma
from .embeddings import create_embeddings
from .loader import load_documents
from .chunking import split_documents

ROOT = Path(__file__).resolve().parents[2]

def open_store(collection="chargegrid_v1"):
    return Chroma(collection_name=collection, embedding_function=create_embeddings(), persist_directory=str(ROOT / "data/chroma"))

def index_documents(size=800, overlap=120, collection="chargegrid_v1"):
    pages = load_documents(ROOT / "data/knowledge_base")
    chunks = split_documents(pages, size, overlap)
    store = open_store(collection)
    # Reindexacao deterministica: evita duplicatas entre execucoes.
    existing = store.get()["ids"]
    if existing:
        store.delete(ids=existing)
    store.add_documents(chunks, ids=[f"chunk_{i}" for i in range(len(chunks))])
    return {"pages": len(pages), "chunks": len(chunks), "collection": collection}
