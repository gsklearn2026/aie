import pytest
from app.services.model_router import router

def test_router_multiple_choice():
    """Test routing for multiple choice questions"""
    profile = router.select_profile(
        question_type="multiple_choice",
        difficulty="medium"
    )
    assert profile == "multiple_choice_expert"

def test_router_essay():
    """Test routing for essay questions"""
    profile = router.select_profile(
        question_type="essay",
        difficulty="hard"
    )
    assert profile == "essay_creative"

def test_router_fallback():
    """Test fallback routing for unknown type"""
    profile = router.select_profile(
        question_type="unknown_type",
        difficulty="medium"
    )
    assert profile == "general_fallback"

def test_fallback_chain():
    """Test fallback chain generation"""
    chain = router.get_fallback_chain("multiple_choice_expert")
    assert len(chain) > 0
    assert "general_fallback" in chain
