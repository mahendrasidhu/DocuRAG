from google import genai
from google.genai import types

from app.config import GEMINI_API_KEY, EMBEDDING_MODEL


client = genai.Client(api_key=GEMINI_API_KEY)


def embed_document(text):
    formatted_text = f"title:none | text:{text}"

    embedding = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=formatted_text
    )

    return embedding.embeddings[0].values

def embed_documents(chunks):
    contents = []

    for chunk in chunks:
        formatted_text = f"title:none | text:{chunk["content"]}"

        content = types.Content(
            parts=[
                types.Part.from_text(text=formatted_text)
            ]
        )

        contents.append(content)

    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=contents
    )

    return [embedding.values for embedding in response.embeddings]

def embed_query(query):
    formatted_text = f"task: search result | query:{query}"

    embedding = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=formatted_text
    )

    return embedding.embeddings[0].values