"""
Template Manager - Core template management functionality
"""
import json
import os
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging
from src.models.template import PromptTemplate, TemplateMetadata, TemplateResponse
from src.templates.validator import TemplateValidator
from src.templates.renderer import TemplateRenderer
from datetime import datetime

logger = logging.getLogger(__name__)

class TemplateManager:
    """Manages template lifecycle and operations"""
    
    def __init__(self, template_dir: str = "templates"):
        self.template_dir = Path(template_dir)
        self.template_dir.mkdir(exist_ok=True)
        self.templates: Dict[str, PromptTemplate] = {}
        self.cache: Dict[str, PromptTemplate] = {}
        self.validator = TemplateValidator()
        self.renderer = TemplateRenderer()
        self._load_templates()
    
    def _load_templates(self) -> None:
        """Load all templates from directory"""
        try:
            for template_file in self.template_dir.glob("*.json"):
                with open(template_file, 'r') as f:
                    template_data = json.load(f)
                    template = PromptTemplate(**template_data)
                    self.templates[template.metadata.name] = template
                    logger.info(f"Loaded template: {template.metadata.name}")
        except Exception as e:
            logger.error(f"Error loading templates: {e}")
    
    def get_template(self, name: str, version: str = "latest") -> Optional[PromptTemplate]:
        """Retrieve template by name and version"""
        if name in self.cache:
            return self.cache[name]
        
        template = self.templates.get(name)
        if template:
            self.cache[name] = template
        return template
    
    def create_template(self, template_data: Dict[str, Any]) -> PromptTemplate:
        """Create new template"""
        # Validate template structure
        validation_errors = self.validator.validate_template_structure(template_data)
        if validation_errors:
            raise ValueError(f"Template validation failed: {validation_errors}")
        
        template = PromptTemplate(**template_data)
        self.templates[template.metadata.name] = template
        
        # Save to file
        self._save_template(template)
        
        # Clear cache for this template
        if template.metadata.name in self.cache:
            del self.cache[template.metadata.name]
        
        logger.info(f"Created template: {template.metadata.name}")
        return template
    
    def update_template(self, name: str, template_data: Dict[str, Any]) -> PromptTemplate:
        """Update existing template"""
        if name not in self.templates:
            raise ValueError(f"Template '{name}' not found")
        
        template_data['metadata']['updated_at'] = datetime.now()
        template = PromptTemplate(**template_data)
        
        self.templates[name] = template
        self._save_template(template)
        
        # Clear cache
        if name in self.cache:
            del self.cache[name]
        
        logger.info(f"Updated template: {name}")
        return template
    
    def delete_template(self, name: str) -> bool:
        """Delete template"""
        if name not in self.templates:
            return False
        
        # Remove from memory
        del self.templates[name]
        if name in self.cache:
            del self.cache[name]
        
        # Remove file
        template_file = self.template_dir / f"{name}.json"
        if template_file.exists():
            template_file.unlink()
        
        logger.info(f"Deleted template: {name}")
        return True
    
    def render_template(self, name: str, variables: Dict[str, Any]) -> TemplateResponse:
        """Render template with variables"""
        template = self.get_template(name)
        if not template:
            raise ValueError(f"Template '{name}' not found")
        
        # Validate variables
        validation_errors = template.validate_variables(variables)
        if validation_errors:
            raise ValueError(f"Variable validation failed: {validation_errors}")
        
        # Render prompt
        rendered_prompt = self.renderer.render(template, variables)
        
        return TemplateResponse(
            template_id=name,
            rendered_prompt=rendered_prompt,
            variables_used=variables,
            metadata=template.metadata
        )
    
    def list_templates(self) -> List[Dict[str, Any]]:
        """List all available templates"""
        return [
            {
                "name": template.metadata.name,
                "version": template.metadata.version,
                "description": template.metadata.description,
                "created_at": template.metadata.created_at,
                "variables": list(template.variables.keys())
            }
            for template in self.templates.values()
        ]
    
    def _save_template(self, template: PromptTemplate) -> None:
        """Save template to file"""
        template_file = self.template_dir / f"{template.metadata.name}.json"
        with open(template_file, 'w') as f:
            json.dump(template.dict(), f, indent=2, default=str)
