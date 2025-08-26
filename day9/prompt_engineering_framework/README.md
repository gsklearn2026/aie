# Prompt Engineering Framework

A production-ready template management system for AI prompts, built as part of the 60-Days AI Engineering series.

## Features

- **Template Management**: Create, update, delete, and version templates
- **Variable Validation**: Type checking and constraint validation
- **Security**: Input sanitization and injection protection  
- **Caching**: Performance optimization with template caching
- **API**: RESTful API for template operations
- **Testing**: Comprehensive test suite with >90% coverage

## Quick Start

### Without Docker

```bash
# Setup environment
./scripts/setup.sh

# Run tests
./scripts/test.sh

# Start application
./scripts/run.sh
```

### With Docker

```bash
# Build and start
docker-compose up --build

# Run tests
docker-compose exec web python -m pytest tests/ -v
```

## API Endpoints

- `GET /api/v1/health` - Health check
- `GET /api/v1/templates` - List all templates
- `GET /api/v1/templates/{name}` - Get specific template
- `POST /api/v1/templates` - Create new template
- `POST /api/v1/templates/{name}/render` - Render template with variables
- `DELETE /api/v1/templates/{name}` - Delete template

## Template Structure

```json
{
  "metadata": {
    "name": "template_name",
    "version": "1.0.0",
    "description": "Template description"
  },
  "prompt": "Your prompt with {variables}",
  "variables": {
    "variable_name": {
      "type": "string|integer|float|boolean|enum",
      "required": true,
      "values": ["option1", "option2"]
    }
  }
}
```

## Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html
```

## Architecture

The system follows a modular architecture:

- **Models**: Pydantic models for data validation
- **Templates**: Core template management logic
- **API**: FastAPI endpoints for REST interface
- **Tests**: Comprehensive test coverage

## Next Steps

This foundation prepares you for Day 10: Question Generation Service, where we'll integrate with AI services for automated content generation.
