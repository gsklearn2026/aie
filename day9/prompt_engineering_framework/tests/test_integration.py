"""
Integration tests for the complete system
"""
import pytest
import tempfile
import shutil
from src.templates.manager import TemplateManager

class TestIntegration:
    
    @pytest.fixture
    def temp_dir(self):
        temp_path = tempfile.mkdtemp()
        yield temp_path
        shutil.rmtree(temp_path)
    
    def test_complete_workflow(self, temp_dir):
        """Test complete template workflow"""
        manager = TemplateManager(template_dir=temp_dir)
        
        # 1. Create a complex template
        template_data = {
            "metadata": {
                "name": "complex_quiz",
                "description": "Complex quiz template with multiple variables",
                "version": "1.0.0"
            },
            "prompt": """Generate a {difficulty} level {question_type} question about {subject}.

Topic: {topic}
Context: {context}

Additional requirements:
- Include {num_options} options if multiple choice
- Provide detailed explanation
- Target audience: {audience}""",
            "variables": {
                "difficulty": {
                    "type": "enum",
                    "values": ["easy", "medium", "hard"],
                    "required": True
                },
                "question_type": {
                    "type": "enum",
                    "values": ["multiple_choice", "true_false", "open_ended"],
                    "required": True
                },
                "subject": {
                    "type": "string",
                    "required": True,
                    "min_length": 2,
                    "max_length": 50
                },
                "topic": {
                    "type": "string",
                    "required": True,
                    "min_length": 3,
                    "max_length": 100
                },
                "context": {
                    "type": "string",
                    "required": False,
                    "max_length": 200
                },
                "num_options": {
                    "type": "integer",
                    "required": False,
                    "default": 4
                },
                "audience": {
                    "type": "string",
                    "required": False,
                    "default": "college students"
                }
            }
        }
        
        # 2. Create template
        template = manager.create_template(template_data)
        assert template.metadata.name == "complex_quiz"
        
        # 3. Test rendering with various inputs
        test_cases = [
            {
                "difficulty": "medium",
                "question_type": "multiple_choice",
                "subject": "Computer Science",
                "topic": "Binary Search Trees",
                "context": "Data structures in programming",
                "num_options": 4,
                "audience": "undergraduate students"
            },
            {
                "difficulty": "hard",
                "question_type": "open_ended",
                "subject": "Software Engineering",
                "topic": "Design Patterns",
                "context": "Object-oriented programming"
            }
        ]
        
        for variables in test_cases:
            response = manager.render_template("complex_quiz", variables)
            
            # Verify response structure
            assert response.template_id == "complex_quiz"
            assert response.rendered_prompt is not None
            assert len(response.rendered_prompt) > 0
            assert response.variables_used == variables
            
            # Verify variable substitution
            for var_name, var_value in variables.items():
                if var_name in ["num_options"] and var_value:
                    assert str(var_value) in response.rendered_prompt
                elif isinstance(var_value, str):
                    assert var_value in response.rendered_prompt
        
        # 4. Test template management operations
        templates = manager.list_templates()
        assert len(templates) == 1
        assert templates[0]["name"] == "complex_quiz"
        
        # 5. Test template retrieval
        retrieved = manager.get_template("complex_quiz")
        assert retrieved is not None
        assert retrieved.metadata.name == "complex_quiz"
        
        # 6. Test validation with invalid input
        invalid_variables = {
            "difficulty": "impossible",  # Invalid enum value
            "question_type": "multiple_choice",
            "subject": "CS",
            "topic": "Trees"
        }
        
        with pytest.raises(ValueError, match="validation"):
            manager.render_template("complex_quiz", invalid_variables)
