from app.ingestion import discover_documents, load_document
from app.chunking import chunk_document
from app.embeddings import embed_documents


def build_all_documents():
    knowledge_base = []

    for file in discover_documents():
        content = load_document(file)
        filename = file.name
        chunks = chunk_document(content)
        embeddings = embed_documents(chunks)

        for index, chunk in enumerate(chunks):
            knowledge_base.append({
                "point_id":f"{filename}_{chunk["chunk_id"]}",
                "chunk_id": chunk["chunk_id"],
                "page_number" :chunk["page_number"],
                "filename": filename,
                "content": chunk["content"],
                "embedding": embeddings[index]
            })

    return knowledge_base