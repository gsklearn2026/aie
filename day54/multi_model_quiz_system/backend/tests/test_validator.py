import pytest
from app.services.quality_validator import validator

def test_validate_multiple_choice():
    """Test multiple choice validation"""
    question = {
        "question": "What is Python?",
        "options": ["A) Language", "B) Snake", "C) Tool", "D) Framework"],
        "correct_answer": "A",
        "explanation": "Python is a programming language"
    }
    score = validator.validate_question(question, "multiple_choice")
    assert score >= 4.0

def test_validate_missing_fields():
    """Test validation with missing fields"""
    question = {
        "question": "What is Python?"
    }
    score = validator.validate_question(question, "multiple_choice")
    assert score < 3.0

def test_validate_true_false():
    """Test true/false validation"""
    question = {
        "question": "Python is a programming language",
        "correct_answer": "true",
        "explanation": "Python is indeed a programming language"
    }
    score = validator.validate_question(question, "true_false")
    assert score >= 4.0
