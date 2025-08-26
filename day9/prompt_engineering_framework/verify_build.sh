#!/bin/bash

echo "🔍 Verifying Complete Build..."
echo "================================="

# Check Python version
python_version=$(python3 --version 2>&1)
echo "✅ Python version: $python_version"

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "✅ Virtual environment created"
else
    echo "❌ Virtual environment missing"
    exit 1
fi

# Check if all required files exist
required_files=(
    "main.py"
    "requirements.txt"
    "src/models/template.py"
    "src/templates/manager.py"
    "src/api/endpoints.py"
    "templates/multiple_choice.json"
    "tests/test_template_model.py"
    "Dockerfile"
    "docker-compose.yml"
)

missing_files=0
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ Found: $file"
    else
        echo "❌ Missing: $file"
        missing_files=$((missing_files + 1))
    fi
done

if [ $missing_files -gt 0 ]; then
    echo "❌ Build incomplete: $missing_files files missing"
    exit 1
fi

echo ""
echo "🎉 Build verification successful!"
echo "📁 Project structure complete"
echo "🧪 Tests available"
echo "🐳 Docker configuration ready"
echo "🚀 Ready for development!"

echo ""
echo "Next steps:"
echo "1. Run: source venv/bin/activate"
echo "2. Run: python -m pytest tests/ -v"
echo "3. Run: python main.py"
echo "4. Visit: http://localhost:8000/docs"
