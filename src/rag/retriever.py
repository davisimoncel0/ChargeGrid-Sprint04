from .vector_store import open_store

def retrieve(question, k=4, collection="chargegrid_v1"):
    return open_store(collection).similarity_search_with_relevance_scores(question, k=k)
