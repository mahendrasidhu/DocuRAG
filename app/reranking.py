from sentence_transformers import CrossEncoder
from app.config import CROSS_ENCODER_MODEL

model=CrossEncoder(CROSS_ENCODER_MODEL)

def rerank(query,results,limit=5):
    pairs =[
        (query,result.content)
        for result in results
    ]
    
    scores = model.predict(pairs)
    
    for index,result in enumerate(results):
        results[index]=result.model_copy(
            update={"rerank_score":scores[index]}
        )
        
    sorted_results=sorted(
        results,
        key=lambda x:x.rerank_score,
        reverse=True
    )
    
    return sorted_results[:limit]