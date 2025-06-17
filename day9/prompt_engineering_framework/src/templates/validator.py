"""
Template Validator - Validation logic for templates and variables
"""
import re
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class TemplateValidator:
    """Validates template structure and variable inputs"""
    
    def __init__(self):
        self.security_patterns = [
            r'<script.*?>.*?</script>',  # Script tags
            r'javascript:',  # JavaScript URLs
            r'on\w+\s*=',    # Event handlers
            r'eval\s*\(',    # Eval calls
        ]
    
    def validate_template_structure(self, template_data: Dict[str, Any]) -> List[str]:
        """Validate template structure"""
        errors = []
        
        # Check required fields
        if 'metadata' not in template_data:
            errors.append("Missing 'metadata' field")
        elif 'name' not in template_data['metadata']:
            errors.append("Missing 'metadata.name' field")
        
        if 'prompt' not in template_data:
            errors.append("Missing 'prompt' field")
        elif not template_data['prompt'].strip():
            errors.append("Empty prompt not allowed")
        
        # Validate variable placeholders in prompt
        if 'prompt' in template_data and 'variables' in template_data:
            errors.extend(self._validate_prompt_variables(
                template_data['prompt'], 
                template_data['variables']
            ))
        
        return errors
    
    def validate_input_security(self, value: str) -> List[str]:
        """Check input for security issues"""
        errors = []
        
        for pattern in self.security_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                errors.append(f"Potentially malicious content detected")
                break
        
        return errors
    
    def sanitize_input(self, value: str) -> str:
        """Sanitize input value"""
        # Remove potentially dangerous content
        sanitized = value
        for pattern in self.security_patterns:
            sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
        
        # Basic HTML entity encoding
        sanitized = sanitized.replace('<', '&lt;').replace('>', '&gt;')
        
        return sanitized.strip()
    
    def _validate_prompt_variables(self, prompt: str, variables: Dict[str, Any]) -> List[str]:
        """Validate that prompt variables match defined variables"""
        errors = []
        
        # Find all variable placeholders in prompt
        placeholder_pattern = r'\{(\w+)\}'
        placeholders = set(re.findall(placeholder_pattern, prompt))
        
        # Check if all placeholders have corresponding variable definitions
        defined_variables = set(variables.keys())
        
        missing_definitions = placeholders - defined_variables
        if missing_definitions:
            errors.append(f"Undefined variables in prompt: {missing_definitions}")
        
        unused_definitions = defined_variables - placeholders
        if unused_definitions:
            errors.append(f"Defined but unused variables: {unused_definitions}")
        
        return errors
