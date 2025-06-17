"""
Template Renderer - Handles prompt rendering with variables
"""
import re
from typing import Dict, Any
from src.models.template import PromptTemplate
import logging

logger = logging.getLogger(__name__)

class TemplateRenderer:
    """Renders templates with variable substitution"""
    
    def __init__(self):
        self.placeholder_pattern = r'\{(\w+)\}'
    
    def render(self, template: PromptTemplate, variables: Dict[str, Any]) -> str:
        """Render template with variables"""
        try:
            # Start with base prompt
            rendered = template.prompt
            
            # Apply system prompt if exists
            if template.system_prompt:
                rendered = f"{template.system_prompt}\n\n{rendered}"
            
            # Substitute variables
            rendered = self._substitute_variables(rendered, variables)
            
            # Apply any post-processing
            rendered = self._post_process(rendered)
            
            logger.debug(f"Rendered template: {template.metadata.name}")
            return rendered
            
        except Exception as e:
            logger.error(f"Error rendering template: {e}")
            raise
    
    def _substitute_variables(self, prompt: str, variables: Dict[str, Any]) -> str:
        """Substitute variable placeholders with actual values"""
        def replace_placeholder(match):
            var_name = match.group(1)
            if var_name in variables:
                value = variables[var_name]
                # Convert value to string with appropriate formatting
                if isinstance(value, list):
                    return ', '.join(str(item) for item in value)
                elif isinstance(value, dict):
                    return str(value)  # Could be improved with JSON formatting
                else:
                    return str(value)
            else:
                # Keep placeholder if variable not found (should not happen after validation)
                return match.group(0)
        
        return re.sub(self.placeholder_pattern, replace_placeholder, prompt)
    
    def _post_process(self, rendered: str) -> str:
        """Apply post-processing to rendered prompt"""
        # Clean up extra whitespace
        rendered = re.sub(r'\n\s*\n\s*\n', '\n\n', rendered)
        rendered = rendered.strip()
        
        return rendered
