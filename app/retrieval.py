from app.embeddings import embed_query
from app.vector_store import search_qdrant
from app.models import SearchResult

def retrieve(query,limit=5):
    query_embedding=embed_query(query)
    
    results=search_qdrant(
        query_embedding,
        limit=limit
    )
    
    search_results=[]
    
    for point in results:
        search_results.append(
            SearchResult(
                content=point.payload["content"],
                filename=point.payload["filename"],
                chunk_id=point.payload["chunk_id"],
                page_number=point.payload.get("page_number"),
                score=point.score
            )
        )
    
    return search_results



def filter_relevant(results, threshold):
    return [
        result for result in results
        if result.rerank_score>=threshold
    ]
    