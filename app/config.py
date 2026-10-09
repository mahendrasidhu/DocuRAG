import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

EMBEDDING_MODEL = "gemini-embedding-2"
GENERATION_MODEL = "gemini-3.1-flash-lite"
CROSS_ENCODER_MODEL="cross-encoder/ms-marco-MiniLM-L6-v2"

QDRANT_COLLECTION = "documents"
VECTOR_SIZE = 3072
DOCUMENTS_DIR = "documents"

RERANK_THRESHOLD=3.0
CHUNK_SIZE=500
CHUNK_OVERLAP=100