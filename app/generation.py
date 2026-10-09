from app.config import GENERATION_MODEL,GEMINI_API_KEY
from google import genai

client = genai.Client(api_key=GEMINI_API_KEY)

def generate_answer(query,results):
    
    res=""
    
    for item in results:
        res+=f"""\n \n
                 source:{item.filename}\n
                 page number:{item.page_number}\n
                 {item.content}
                 """
        
    prompt=f"""
    You are RAG ChatBot.
    Answer only from the documents provided below.
    Don't use your own knowledge to answer the questions.
    If the provided documents do not contain enough information to answer the query, say:
    "The provided documents do not contain enough information to answer this question."
    
    Provided information:{res}
    
    query: {query}
    """
    
    response=client.models.generate_content(
        model=GENERATION_MODEL,
        contents=prompt
    )
    
    
    return response.text