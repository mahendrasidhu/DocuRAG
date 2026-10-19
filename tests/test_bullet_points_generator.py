import pytest
from app.bullet_points_generator import validate_bullet_points


def test_validate_bullet_points_accepts_valid_points():
    result = {
        "bullet_points": [
            "RAG combines retrieval and text generation.",
            "A retriever searches for relevant information."
        ]
    }

    validated = validate_bullet_points(result)

    assert validated == result


def test_validate_bullet_points_rejects_missing_field():
    result = {}

    with pytest.raises(ValueError):
        validate_bullet_points(result)


def test_validate_bullet_points_rejects_empty_point():
    result = {
        "bullet_points": [
            "RAG combines retrieval and generation.",
            "   "
        ]
    }

    with pytest.raises(ValueError):
        validate_bullet_points(result)