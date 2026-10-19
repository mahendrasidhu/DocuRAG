from app.reranking import rerank
from app.retrieval import retrieve,filter_relevant
from app.generation import generate_answer
from app.config import RERANK_THRESHOLD
from app.contextualizer import contextualize_query

def ask(query,history=None):
    if history is None:
        history=[]
    
    contextualized_query = contextualize_query(query,history)
    
    results=retrieve(contextualized_query,limit=20)
    
    reranked_results=rerank(contextualized_query,results,limit=5)
    
    filtered_results=filter_relevant(reranked_results,RERANK_THRESHOLD)
    
    sources=[]
    
    if not filtered_results:
        answer="I'm unable to answer from the provided documents."
    
    else:
        answer=generate_answer(contextualized_query,filtered_results)
        for result in filtered_results:
            sources.append({
                "filename" : result.filename,
                "page_number": result.page_number,
                "chunk_id": result.chunk_id
            })
            
    print("Original query:", query)
    print("Conversation history:", history)
    print("Contextualized query:", contextualized_query)
    
    return{ 
    "answer": answer,
    "sources": sources
    }