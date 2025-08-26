"""
Tests for template manager
"""
import pytest
import tempfile
import shutil
from pathlib import Path
from src.templates.manager import TemplateManager
from src.models.template import TemplateMetadata

class TestTemplateManager:
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests"""
        temp_path = tempfile.mkdtemp()
        yield temp_path
        shutil.rmtree(temp_path)
    
    @pytest.fixture
    def manager(self, temp_dir):
        """Create template manager with temp directory"""
        return TemplateManager(template_dir=temp_dir)
    
    def test_create_template(self, manager):
        """Test template creation"""
        template_data = {
            "metadata": {
                "name": "test_template",
                "description": "Test template"
            },
            "prompt": "Hello {name}!",
            "variables": {
                "name": {
                    "type": "string",
                    "required": True
                }
            }
        }
        
        template = manager.create_template(template_data)
        assert template.metadata.name == "test_template"
        assert "test_template" in manager.templates
    
    def test_get_template(self, manager):
        """Test template retrieval"""
        template_data = {
            "metadata": {"name": "test_get"},
            "prompt": "Test prompt",
            "variables": {}
        }
        
        manager.create_template(template_data)
        retrieved = manager.get_template("test_get")
        
        assert retrieved is not None
        assert retrieved.metadata.name == "test_get"
    
    def test_render_template(self, manager):
        """Test template rendering through manager"""
        template_data = {
            "metadata": {"name": "render_test"},
            "prompt": "Hello {name}, welcome to {course}!",
            "variables": {
                "name": {"type": "string", "required": True},
                "course": {"type": "string", "required": True}
            }
        }
        
        manager.create_template(template_data)
        
        variables = {"name": "Bob", "course": "AI Engineering"}
        response = manager.render_template("render_test", variables)
        
        assert response.template_id == "render_test"
        assert "Hello Bob, welcome to AI Engineering!" in response.rendered_prompt
    
    def test_list_templates(self, manager):
        """Test template listing"""
        # Create multiple templates
        for i in range(3):
            template_data = {
                "metadata": {"name": f"template_{i}"},
                "prompt": f"Template {i}",
                "variables": {}
            }
            manager.create_template(template_data)
        
        templates = manager.list_templates()
        assert len(templates) == 3
        
        names = [t["name"] for t in templates]
        assert "template_0" in names
        assert "template_1" in names
        assert "template_2" in names
    
    def test_delete_template(self, manager):
        """Test template deletion"""
        template_data = {
            "metadata": {"name": "delete_test"},
            "prompt": "To be deleted",
            "variables": {}
        }
        
        manager.create_template(template_data)
        assert "delete_test" in manager.templates
        
        success = manager.delete_template("delete_test")
        assert success
        assert "delete_test" not in manager.templates
