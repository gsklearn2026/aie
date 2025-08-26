"""
Template data models for the prompt engineering framework
"""
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field, validator
from enum import Enum
import json
from datetime import datetime

class VariableType(str, Enum):
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    ENUM = "enum"
    LIST = "list"

class VariableSchema(BaseModel):
    """Schema definition for template variables"""
    type: VariableType
    required: bool = True
    default: Optional[Union[str, int, float, bool, List[Any]]] = None
    values: Optional[List[str]] = None  # For enum type
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    pattern: Optional[str] = None
    description: Optional[str] = None

    @validator('values')
    def validate_enum_values(cls, v, values):
        if values.get('type') == VariableType.ENUM and not v:
            raise ValueError("Enum type requires 'values' list")
        return v

class TemplateMetadata(BaseModel):
    """Template metadata"""
    name: str = Field(..., min_length=1, max_length=100)
    version: str = Field(default="1.0.0")
    description: Optional[str] = None
    author: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    tags: List[str] = Field(default_factory=list)

class PromptTemplate(BaseModel):
    """Main template model"""
    metadata: TemplateMetadata
    prompt: str = Field(..., min_length=1)
    variables: Dict[str, VariableSchema] = Field(default_factory=dict)
    expected_format: str = Field(default="text")
    system_prompt: Optional[str] = None
    examples: List[Dict[str, Any]] = Field(default_factory=list)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

    def validate_variables(self, input_vars: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate input variables against schema"""
        errors = {}
        
        for var_name, schema in self.variables.items():
            if schema.required and var_name not in input_vars:
                errors.setdefault(var_name, []).append("Required variable missing")
                continue
                
            if var_name not in input_vars:
                continue
                
            value = input_vars[var_name]
            var_errors = []
            
            # Type validation
            if schema.type == VariableType.STRING and not isinstance(value, str):
                var_errors.append("Must be a string")
            elif schema.type == VariableType.INTEGER and not isinstance(value, int):
                var_errors.append("Must be an integer")
            elif schema.type == VariableType.FLOAT and not isinstance(value, (int, float)):
                var_errors.append("Must be a number")
            elif schema.type == VariableType.BOOLEAN and not isinstance(value, bool):
                var_errors.append("Must be a boolean")
            elif schema.type == VariableType.ENUM and value not in (schema.values or []):
                var_errors.append(f"Must be one of: {schema.values}")
            
            # Length validation for strings
            if schema.type == VariableType.STRING and isinstance(value, str):
                if schema.min_length and len(value) < schema.min_length:
                    var_errors.append(f"Minimum length: {schema.min_length}")
                if schema.max_length and len(value) > schema.max_length:
                    var_errors.append(f"Maximum length: {schema.max_length}")
            
            if var_errors:
                errors[var_name] = var_errors
        
        return errors

    def render(self, variables: Dict[str, Any]) -> str:
        """Render template with variables"""
        # Validate first
        validation_errors = self.validate_variables(variables)
        if validation_errors:
            raise ValueError(f"Validation errors: {validation_errors}")
        
        # Simple variable substitution (in production, use Jinja2)
        rendered = self.prompt
        for var_name, value in variables.items():
            placeholder = "{" + var_name + "}"
            rendered = rendered.replace(placeholder, str(value))
        
        return rendered

class TemplateResponse(BaseModel):
    """Response model for template operations"""
    template_id: str
    rendered_prompt: str
    variables_used: Dict[str, Any]
    metadata: TemplateMetadata
    timestamp: datetime = Field(default_factory=datetime.now)
