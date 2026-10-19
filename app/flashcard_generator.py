
from google import genai
from app.config import GEMINI_API_KEY, GENERATION_MODEL
import json

client = genai.Client(api_key=GEMINI_API_KEY)


def validate_flashcards(flashcards):
    if not isinstance(flashcards, dict):
        raise ValueError("Flashcard response must be a JSON object.")

    if "flashcards" not in flashcards:
        raise ValueError("Response is missing the 'flashcards' field.")

    cards = flashcards["flashcards"]

    if not isinstance(cards, list) or not cards:
        raise ValueError("Flashcards must contain a non-empty list.")

    for index, card in enumerate(cards, start=1):
        if not isinstance(card, dict):
            raise ValueError(f"Flashcard {index} must be a JSON object.")

        required_fields = {"question", "answer"}

        if not required_fields.issubset(card):
            raise ValueError(
                f"Flashcard {index} is missing required fields."
            )

        if not isinstance(card["question"], str) or not card["question"].strip():
            raise ValueError(f"Flashcard {index} has an invalid question.")

        if not isinstance(card["answer"], str) or not card["answer"].strip():
            raise ValueError(f"Flashcard {index} has an invalid answer.")

    return flashcards


def generate_flashcards(context, num_cards=10):
    prompt = f"""
    You are a flashcard generator for a document-based study application.

    Use ONLY the document content provided below.
    Do not introduce facts from your general knowledge.

    Generate {num_cards} flashcards.

    For every flashcard, provide:
    - question: a clear prompt that tests recall of a concept
    - answer: a concise answer supported by the document

    Make sure:
    - Questions test meaningful concepts, facts, or definitions.
    - Answers are accurate and grounded in the document.
    - Questions do not repeatedly test the same fact.
    - Return valid JSON only, without Markdown code fences.

    Required JSON structure:
    {{
        "flashcards": [
            {{
                "question": "Example question",
                "answer": "Example answer"
            }}
        ]
    }}

    Document content:
    {context}
    """

    response = client.models.generate_content(
        model=GENERATION_MODEL,
        contents=prompt,
    )

    flashcards = json.loads(response.text)

    return validate_flashcards(flashcards)
