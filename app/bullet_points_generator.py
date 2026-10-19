from google import genai
from app.config import GEMINI_API_KEY, GENERATION_MODEL
import json

client = genai.Client(api_key=GEMINI_API_KEY)

def validate_bullet_points(result):
    if not isinstance(result, dict):
        raise ValueError("Response must be a JSON object.")

    if "bullet_points" not in result:
        raise ValueError("Response is missing the 'bullet_points' field.")

    points = result["bullet_points"]

    if not isinstance(points, list) or not points:
        raise ValueError("Bullet points must be a non-empty list.")

    for index, point in enumerate(points, start=1):
        if not isinstance(point, str) or not point.strip():
            raise ValueError(
                f"Bullet point {index} must be a non-empty string."
            )

    return result


def generate_bullet_points(context, num_points=10):
    prompt = f"""
    You are a document summarization assistant for a study application.

    Use ONLY the document content provided below.
    Do not introduce facts from your general knowledge.
    Do not make claims that are unsupported by the document.

    Generate approximately {num_points} important bullet points.

    Focus on:
    - Key concepts and definitions
    - Important facts and explanations
    - Processes, methods, and their purposes
    - Relationships between concepts

    Make sure:
    - Each bullet point communicates one main idea.
    - Each point is concise but preserves important meaning.
    - Avoid repeating the same information.
    - Cover the most important information in the document.
    - Return valid JSON only, without Markdown code fences.

    Required JSON structure:
    {{
        "bullet_points": [
            "First important point",
            "Second important point"
        ]
    }}

    Document content:
    {context}
    """

    response = client.models.generate_content(
        model=GENERATION_MODEL,
        contents=prompt,
    )

    result = json.loads(response.text)

    return validate_bullet_points(result)