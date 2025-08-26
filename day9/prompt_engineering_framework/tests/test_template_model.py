"""
Tests for template models
"""
import pytest
from datetime import datetime
from src.models.template import (
    PromptTemplate, TemplateMetadata, VariableSchema, VariableType
)

class TestTemplateModel:
    
    def test_create_simple_template(self):
        """Test creating a basic template"""
        metadata = TemplateMetadata(name="test_template")
        template = PromptTemplate(
            metadata=metadata,
            prompt="Hello {name}!",
            variables={
                "name": VariableSchema(type=VariableType.STRING)
            }
        )
        
        assert template.metadata.name == "test_template"
        assert template.prompt == "Hello {name}!"
        assert "name" in template.variables
    
    def test_variable_validation_success(self):
        """Test successful variable validation"""
        metadata = TemplateMetadata(name="test")
        template = PromptTemplate(
            metadata=metadata,
            prompt="Question about {subject} with {difficulty} level",
            variables={
                "subject": VariableSchema(type=VariableType.STRING, required=True),
                "difficulty": VariableSchema(
                    type=VariableType.ENUM, 
                    values=["easy", "medium", "hard"],
                    required=True
                )
            }
        )
        
        variables = {"subject": "Python", "difficulty": "medium"}
        errors = template.validate_variables(variables)
        assert len(errors) == 0
    
    def test_variable_validation_missing_required(self):
        """Test validation with missing required variable"""
        metadata = TemplateMetadata(name="test")
        template = PromptTemplate(
            metadata=metadata,
            prompt="Hello {name}!",
            variables={
                "name": VariableSchema(type=VariableType.STRING, required=True)
            }
        )
        
        errors = template.validate_variables({})
        assert "name" in errors
        assert "Required variable missing" in errors["name"]
    
    def test_template_rendering(self):
        """Test template rendering"""
        metadata = TemplateMetadata(name="test")
        template = PromptTemplate(
            metadata=metadata,
            prompt="Hello {name}, you are learning {subject}!",
            variables={
                "name": VariableSchema(type=VariableType.STRING),
                "subject": VariableSchema(type=VariableType.STRING)
            }
        )
        
        variables = {"name": "Alice", "subject": "AI Engineering"}
        rendered = template.render(variables)
        assert rendered == "Hello Alice, you are learning AI Engineering!"
    
    def test_enum_validation(self):
        """Test enum variable validation"""
        metadata = TemplateMetadata(name="test")
        template = PromptTemplate(
            metadata=metadata,
            prompt="Difficulty: {level}",
            variables={
                "level": VariableSchema(
                    type=VariableType.ENUM,
                    values=["easy", "medium", "hard"]
                )
            }
        )
        
        # Valid enum value
        errors = template.validate_variables({"level": "medium"})
        assert len(errors) == 0
        
        # Invalid enum value
        errors = template.validate_variables({"level": "impossible"})
        assert "level" in errors
