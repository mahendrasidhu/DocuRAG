from app.index_metadata import load_metadata, save_metadata, calculate_hash
from app.ingestion import discover_documents,load_document
from app.chunking import chunk_document
from app.embeddings import embed_documents
from app.vector_store import index_documents,delete_document

def get_document_changes():
    existing_metadata=load_metadata()
    new_metadata={}
    files=discover_documents()
    
    for file in files:
        content=load_document(file)
        file_hash=calculate_hash(content)
        filename=file.name
        file_metadata={
            "hash":file_hash
        }
        
        new_metadata[filename] = file_metadata
        
    existing_files=set(existing_metadata)
    new_files=set(new_metadata)
    
    added_files=new_files-existing_files
    removed_files=existing_files-new_files
    changed_files={
        filename for filename in existing_files & new_files
        if existing_metadata[filename]["hash"] != new_metadata[filename]["hash"]
    }
    
    unchanged_files={
        filename for filename in existing_files & new_files
        if existing_metadata[filename]["hash"] == new_metadata[filename]["hash"]
    }
    
    return {
        "added": added_files,
        "removed": removed_files,
        "changed": changed_files,
        "unchanged": unchanged_files,
        "new_metadata":new_metadata
    }
    
    
def index_new_document(file):
    content=load_document(file)
    chunks=chunk_document(content)
    embeddings=embed_documents(chunks)
    filename=file.name
    knowledge_base=[]
    
    for index,chunk in enumerate(chunks):
        knowledge_base.append({
            "point_id":f"{filename}_{index}",
            "chunk_id":index,
            "filename":filename,
            "content":chunk,
            "embedding":embeddings[index]
        })
    
    index_documents(knowledge_base)
    
def update_document(file):
    content=load_document(file)
    chunks=chunk_document(content)
    embeddings=embed_documents(chunks)
    filename=file.name
    
    delete_document(filename)
    
    knowledge_base=[]
    
    for index,chunk in enumerate(chunks):
            knowledge_base.append({
                "point_id":f"{filename}_{index}",
                "chunk_id":index,
                "filename":filename,
                "content":chunk,
                "embedding":embeddings[index]
            })
    index_documents(knowledge_base)
    
def update_index():
    changes=get_document_changes()
    files={
        file.name:file
        for file in discover_documents()
    }
    metadata=load_metadata()
    
    for filename in changes["added"]:
        file=files[filename]
        index_new_document(file)
        metadata[filename]=changes["new_metadata"][filename]
        print(f"Indexing new document: {filename}")
        
        
    for filename in changes["changed"]:
        file= files[filename]
        update_document(file)
        metadata[filename]=changes["new_metadata"][filename]
        print(f"Updating document: {filename}")
        
            
    for filename in changes["removed"]:
        delete_document(filename)
        metadata.pop(filename)
        print(f"Removing document: {filename}")
        
    
    for filename in changes["unchanged"]:
        print(f"Document unchanged: {filename}")
    
    save_metadata(metadata)