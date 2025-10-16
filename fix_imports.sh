#!/bin/bash
# Fix all imports to use app. prefix

echo "Fixing imports in superkb files..."
find app/superkb -name "*.py" -type f -exec sed -i '' 's/^from graph_rag\./from app.graph_rag./g' {} \;
find app/superkb -name "*.py" -type f -exec sed -i '' 's/^from superscan\./from app.superscan./g' {} \;
find app/superkb -name "*.py" -type f -exec sed -i '' 's/^from superkb\./from app.superkb./g' {} \;
find app/superkb -name "*.py" -type f -exec sed -i '' 's/^from superchat\./from app.superchat./g' {} \;

echo "Fixing imports in superscan files..."
find app/superscan -name "*.py" -type f -exec sed -i '' 's/^from graph_rag\./from app.graph_rag./g' {} \;
find app/superscan -name "*.py" -type f -exec sed -i '' 's/^from superscan\./from app.superscan./g' {} \;
find app/superscan -name "*.py" -type f -exec sed -i '' 's/^from superkb\./from app.superkb./g' {} \;
find app/superscan -name "*.py" -type f -exec sed -i '' 's/^from superchat\./from app.superchat./g' {} \;

echo "Fixing imports in superchat files..."
find app/superchat -name "*.py" -type f -exec sed -i '' 's/^from graph_rag\./from app.graph_rag./g' {} \;
find app/superchat -name "*.py" -type f -exec sed -i '' 's/^from superscan\./from app.superscan./g' {} \;
find app/superchat -name "*.py" -type f -exec sed -i '' 's/^from superkb\./from app.superkb./g' {} \;
find app/superchat -name "*.py" -type f -exec sed -i '' 's/^from superchat\./from app.superchat./g' {} \;

echo "Fixing imports in graph_rag files..."
find app/graph_rag -name "*.py" -type f -exec sed -i '' 's/^from graph_rag\./from app.graph_rag./g' {} \;

echo "Done! All imports fixed."

