import json
from app.retrieval import retrieve
from app.reranking import rerank
def load_dataset():
    with open("Evaluation/dataset.json","r",encoding="utf-8") as file:
        data = json.load(file)
        
    return data


evaluation_questions=load_dataset()
    

def check_recall_at_k(question,k):
    retrieved_results=retrieve(question["query"],limit=20) 
    
    reranked_results=rerank(question["query"],retrieved_results,limit=k)
    
    
    for result in reranked_results:
        
        chunk_id=f"{result.filename}_{result.chunk_id}"
        
        if chunk_id in question["relevant_chunks"]:
            return True
        
    return False
        
def evaluate_retrieval(questions,k=5):
    results={
        "correct":0,
        "total":6,
        "recall":0.0
    }
    
    for q in questions:
        
        
        if check_recall_at_k(q,k=k):
            results["correct"]+=1
            

    results["recall"]=results["correct"]/results["total"]
    
    return results