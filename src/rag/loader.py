from pathlib import Path
from langchain_community.document_loaders import PyMuPDFLoader

def load_documents(folder):
    documents = []
    for path in sorted(Path(folder).glob("*.pdf")):
        for doc in PyMuPDFLoader(str(path)).load():
            doc.metadata["source"] = path.name
            doc.metadata["page"] = int(doc.metadata.get("page", 0)) + 1
            documents.append(doc)
    if not documents:
        raise ValueError("Nenhum PDF encontrado em data/knowledge_base")
    return documents
