from google import genai
from google.genai import types
from app.config import GEMINI_API_KEY,RERANK_THRESHOLD,GENERATION_MODEL
from app.retrieval import retrieve
from app.reranking import rerank
from app.generation import generate_answer
from app.models import GroundingEvaluation

client=genai.Client(api_key=GEMINI_API_KEY)

grounded_questions = [
    "What is Java?",
    "What is inheritance in Java?",
    "What is Python?",
    "How are functions defined in Python?",
    "How does Python define blocks of code?",
    "What data structure stores data as key-value pairs?",
    "What will I be working on in Kotak Tech?",
    "What technologies are used at Kotak Tech?",
    "What does the Scalar AI team include?",
    "What engineering practices are used at Kotak Tech?"
]


def evaluate_generation(questions):
    
    final_results={
        "Grounded":0,
        "Total":len(questions),
        "groundedness":0.0
    }
    
    for query in questions:
        
        results=retrieve(query,limit=10)
        
        reranked_results=rerank(query,results,limit=5)
        
        retrieved_results=[
            result
            for result in reranked_results
            if result.rerank_score>=RERANK_THRESHOLD
        ]
        
        context = ""

        for result in retrieved_results:
            context += f"""
        Source: {result.filename}
        Page: {result.page_number}
        Content:
        {result.content}
        """
        
        answer=generate_answer(query,retrieved_results)
        
        prompt=f"""
        Set grounded to false if the answer contains any factual claim,
        phrase, or assertion that is not supported by the retrieved documents.
        Do not infer or add information that is not explicitly present in the retrieved documents.

        List every unsupported claim in unsupported_claims.

        Do not use outside knowledge.
        Query: {query}
        Answer: {answer}
        Retrieved Documents:{context}
        """
        
        response=client.models.generate_content(
            model=GENERATION_MODEL,
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=GroundingEvaluation
            )
        )
        evaluation=response.parsed
        if evaluation.grounded:
            final_results["Grounded"] += 1
    
    final_results["groundedness"]=final_results["Grounded"]/final_results["Total"]
    
    return final_results

print(evaluate_generation(grounded_questions))