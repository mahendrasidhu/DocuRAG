from app.reranking import rerank
from app.retrieval import retrieve,filter_relevant
from app.generation import generate_answer
from app.config import RERANK_THRESHOLD

def ask(query):
    
    results=retrieve(query,limit=20)
    
    reranked_results=rerank(query,results,limit=5)
    
    filtered_results=filter_relevant(reranked_results,RERANK_THRESHOLD)
    
    source=""
    
    if not filtered_results:
        answer="I'm unable to answer from the provided documents."
    
    else:
        answer=generate_answer(query,filtered_results)
        for result in filtered_results:
            source+=(
                f"- {result.filename}"
                f"-- Page: {result.page_number}"
                f"-- Chunk: {result.chunk_id} \n"
            )
    
    return f"""
Answer:{answer}

Sources:{source}
"""