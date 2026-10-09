from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.ingestion import discover_documents,load_document
from app.config import CHUNK_SIZE,CHUNK_OVERLAP
def chunk_document(document):
    
    splitter=RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    
    final=[]
    
    chunk_id=0
    
    for page in document:
        
        content=page["content"]
        page_number=page["page_number"]
        
        chunks=splitter.split_text(content)
        
        for chunk in chunks:
            answer={
                "chunk_id":chunk_id,
                "page_number":page_number,
                "content":chunk
            }
            
            final.append(answer)
            
            chunk_id+=1
    

    return final
