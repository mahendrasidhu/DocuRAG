import pytest
from app.flashcard_generator import validate_flashcards


def test_validate_flashcards_accepts_valid_cards():
    flashcards = {
        "flashcards": [
            {
                "question": "What is RAG?",
                "answer": "Retrieval-Augmented Generation."
            }
        ]
    }

    result = validate_flashcards(flashcards)

    assert result == flashcards


def test_validate_flashcards_rejects_missing_field():
    flashcards = {}

    with pytest.raises(ValueError):
        validate_flashcards(flashcards)


def test_validate_flashcards_rejects_empty_question():
    flashcards = {
        "flashcards": [
            {
                "question": "   ",
                "answer": "Retrieval-Augmented Generation."
            }
        ]
    }

    with pytest.raises(ValueError):
        validate_flashcards(flashcards)
        