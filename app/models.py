from pydantic import BaseModel

class SearchResult(BaseModel):
    content:str
    filename:str
    page_number:int | None=None
    chunk_id:int
    score:float
    rerank_score: float | None=None
    
    
class GroundingEvaluation(BaseModel):
    grounded: bool
    unsupported_claims: list[str]