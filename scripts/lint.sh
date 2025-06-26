#!/bin/bash

# Run Ruff linter and formatter
echo "🧹 Running Ruff linter..."
.venv/bin/ruff check . --fix

echo "✨ Running Ruff formatter..."
.venv/bin/ruff format .

echo "📊 Final check..."
.venv/bin/ruff check .

if [ $? -eq 0 ]; then
    echo "✅ All checks passed!"
else
    echo "❌ Some issues remain"
fi