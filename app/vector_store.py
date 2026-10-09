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