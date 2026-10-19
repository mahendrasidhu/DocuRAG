import pytest
from app.quiz_generator import validate_quiz


def test_validate_quiz_accepts_valid_quiz():
    quiz = {
        "questions": [
            {
                "question": "What is RAG?",
                "options": [
                    "Retrieval-Augmented Generation",
                    "Random Access Graph",
                    "Rapid Application Generator",
                    "Runtime Agent Gateway",
                ],
                "correct_answer": "Retrieval-Augmented Generation",
                "explanation": "RAG combines retrieval with generation.",
            }
        ]
    }

    result = validate_quiz(quiz)

    assert result == quiz


def test_validate_quiz_rejects_missing_questions():
    quiz = {}

    with pytest.raises(ValueError):
        validate_quiz(quiz)


def test_validate_quiz_rejects_invalid_correct_answer():
    quiz = {
        "questions": [
            {
                "question": "What is RAG?",
                "options": ["A", "B", "C", "D"],
                "correct_answer": "E",
                "explanation": "Test explanation",
            }
        ]
    }

    with pytest.raises(ValueError):
        validate_quiz(quiz)