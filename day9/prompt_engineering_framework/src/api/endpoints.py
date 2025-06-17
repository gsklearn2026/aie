"""
API endpoints for template management
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
from src.templates.manager import TemplateManager
from src.models.template import TemplateResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Dependency to get template manager
def get_template_manager() -> TemplateManager:
    return TemplateManager()

@router.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Prompt Engineering Framework API", "status": "active"}

@router.get("/templates", response_model=List[Dict[str, Any]])
async def list_templates(manager: TemplateManager = Depends(get_template_manager)):
    """List all available templates"""
    try:
        return manager.list_templates()
    except Exception as e:
        logger.error(f"Error listing templates: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/templates/{template_name}")
async def get_template(template_name: str, manager: TemplateManager = Depends(get_template_manager)):
    """Get specific template"""
    try:
        template = manager.get_template(template_name)
        if not template:
            raise HTTPException(status_code=404, detail=f"Template '{template_name}' not found")
        return template.dict()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting template: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/templates", status_code=201)
async def create_template(template_data: Dict[str, Any], manager: TemplateManager = Depends(get_template_manager)):
    """Create new template"""
    try:
        template = manager.create_template(template_data)
        return {"message": "Template created successfully", "template_id": template.metadata.name}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating template: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/templates/{template_name}/render", response_model=TemplateResponse)
async def render_template(
    template_name: str, 
    variables: Dict[str, Any], 
    manager: TemplateManager = Depends(get_template_manager)
):
    """Render template with variables"""
    try:
        response = manager.render_template(template_name, variables)
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error rendering template: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/templates/{template_name}", status_code=204)
async def delete_template(template_name: str, manager: TemplateManager = Depends(get_template_manager)):
    """Delete template"""
    try:
        success = manager.delete_template(template_name)
        if not success:
            raise HTTPException(status_code=404, detail=f"Template '{template_name}' not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting template: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "prompt-engineering-framework"}
