from app.config import GENERATION_MODEL,GEMINI_API_KEY
from google import genai
import json

client=genai.Client(api_key=GEMINI_API_KEY)

def validate_quiz(quiz):
    
    if "questions" not in quiz:
        raise ValueError("Quiz response is missing the Questions field.")
    
    questions=quiz["questions"]
    
    if not isinstance(questions,list) or not questions:
        raise ValueError("Quiz must contain non-empty questions list.")
    
    for index,question in enumerate(questions, start=1):
        required_fields={
            "question","options","correct_answer","explanation"
        }
        
        if not required_fields.issubset(question):
            raise ValueError(f"Question {index} is missing required fields.")
        
        options=question["options"]
        
        if not isinstance(options, list) or len(options)!=4:
            raise ValueError(f"Question {index} must have only 4 options.")
        
        if question["correct_answer"] not in options:
            raise ValueError(f"Question {index} has correct answer not present in its options.")
        
    return quiz


def generate_quiz(context, num_questions=5):
    prompt = f"""
    You are a quiz generator for a document-based study application.

    Use ONLY the document content provided below.
    Do not introduce facts from your general knowledge.

    Generate {num_questions} multiple-choice questions.

    For every question, provide:
    - question: the question text
    - options: exactly four possible answers
    - correct_answer: the exact text of the correct option
    - explanation: a brief explanation supported by the document

    Make sure:
    - Only one option is correct.
    - Incorrect options are plausible.
    - Every correct answer is supported by the document.
    - Questions do not repeat the same fact.
    - Return valid JSON only, without Markdown code fences.

    Document content:
    {context}
    """

    response = client.models.generate_content(
        model=GENERATION_MODEL,
        contents=prompt,
    )

    quiz = json.loads(response.text)
    
    return validate_quiz(quiz)