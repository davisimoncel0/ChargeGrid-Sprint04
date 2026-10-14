from langchain_text_splitters import RecursiveCharacterTextSplitter

def split_documents(documents, size=800, overlap=120):
    return RecursiveCharacterTextSplitter(chunk_size=size, chunk_overlap=overlap).split_documents(documents)
