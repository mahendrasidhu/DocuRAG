from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams,PointStruct,Filter, FieldCondition, MatchValue, FilterSelector
import uuid

from app.config import VECTOR_SIZE, QDRANT_COLLECTION


qdrant= QdrantClient(path="qdrant_storage")
if not qdrant.collection_exists(QDRANT_COLLECTION):
    qdrant.create_collection(
        collection_name=QDRANT_COLLECTION,
        vectors_config=VectorParams(
            size=VECTOR_SIZE,
            distance=Distance.COSINE
        )
    )

def index_documents(knowledge_base):
    points=[]
    for item in knowledge_base:
        point_id=str(uuid.uuid5(uuid.NAMESPACE_URL,item["point_id"]))
        point=PointStruct(
            id=point_id,
            vector=item["embedding"],
            payload={
                "point_id": item["point_id"],
                "chunk_id":item["chunk_id"],
                "page_number":item["page_number"],
                "content":item["content"],
                "filename":item["filename"]
            }
        )
        
        points.append(point)
        
    qdrant.upsert(
        collection_name=QDRANT_COLLECTION,
        points=points
    )
        
def search_qdrant(query_embedding,limit=2):
    
    results=qdrant.query_points(
        collection_name=QDRANT_COLLECTION,
        query=query_embedding,
        limit=limit
    )
    
    return results.points

def delete_document(filename):
    qdrant.delete(
        collection_name=QDRANT_COLLECTION,
        points_selector=FilterSelector(
            filter=Filter(
                must=[
                    FieldCondition(
                        key="filename",
                        match=MatchValue(value=filename)
                    )
                ]
            )
        ),
    )
    
    

def get_indexed_filenames():
    filenames = set()
    offset = None

    while True:
        points, offset = qdrant.scroll(
            collection_name=QDRANT_COLLECTION,
            limit=100,
            offset=offset,
            with_payload=["filename"],
            with_vectors=False
        )

        for point in points:
            filename = point.payload.get("filename")
            if filename:
                filenames.add(filename)

        if offset is None:
            break

    return filenames

def get_document_chunks(filename):
    
    chunks=[]
    offset = None
    
    while True:
        points,offset=qdrant.scroll(
            collection_name=QDRANT_COLLECTION,
            scroll_filter=Filter(
                must=[
                    FieldCondition(
                        key="filename",
                        match=MatchValue(value=filename)
                    )
                ]
            ),
            limit=100,
            offset=offset,
            with_payload=True,
            with_vectors=False            
        )
        
        for point in points:
            chunks.append(point.payload)
            
        if offset is None:
            break
    
    chunks.sort(key=lambda chunk: chunk["chunk_id"])
    
    return chunks


def close_vector_store():
    qdrant.close()