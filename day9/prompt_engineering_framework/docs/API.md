# API Documentation

## Authentication

Currently, no authentication is required. In production, implement proper authentication mechanisms.

## Error Responses

All endpoints return structured error responses:

```json
{
  "detail": "Error message",
  "status_code": 400
}
```

## Template Operations

### Create Template

```bash
curl -X POST http://localhost:8000/api/v1/templates \
  -H "Content-Type: application/json" \
  -d '{
    "metadata": {
      "name": "my_template",
      "description": "Custom template"
    },
    "prompt": "Generate a {type} about {topic}",
    "variables": {
      "type": {"type": "string", "required": true},
      "topic": {"type": "string", "required": true}
    }
  }'
```

### Render Template

```bash
curl -X POST http://localhost:8000/api/v1/templates/my_template/render \
  -H "Content-Type: application/json" \
  -d '{
    "type": "question",
    "topic": "AI Engineering"
  }'
```
