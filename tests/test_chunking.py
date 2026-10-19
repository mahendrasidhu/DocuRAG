from app.chunking import chunk_document


from app.chunking import chunk_document

def test_content_preservation():
    original_text = "Python is a user-friendly coding language. It is used by millions of people daily."

    document = [
        {
            "page_number": 1,
            "content": original_text
        }
    ]

    chunks = chunk_document(document)

    assert len(chunks) > 0

    combined_content = "".join(chunk["content"] for chunk in chunks)

    assert combined_content == original_text

    
def test_chunk_id():
    document=[
        {
            "page_number":0,
            "content":"A"*1200
        }
    ]
    
    chunks=chunk_document(document)
    
    ids=[chunk['chunk_id'] for chunk in chunks]  
        
    assert ids==[0,1,2]
    
def test_page():
    
    document=[
            {
                "page_number":3,
                "content":"Python is User-friendly coding language. It is used by millions of people daily."
            }
        ]
    
    chunks=chunk_document(document)
    
    assert chunks[0]["page_number"]==document[0]["page_number"]