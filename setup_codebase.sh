#!/bin/bash
# Setup script to ensure proper codebase structure for development and deployment

echo "🚀 Setting up SuperSuite codebase structure..."

# Create symlink for app/code if it doesn't exist
if [ ! -L "app/code" ]; then
    echo "📁 Creating symlink: app/code -> code"
    ln -s ../code app/code
else
    echo "✅ Symlink app/code already exists"
fi

# Create bin directory if it doesn't exist
if [ ! -d "bin" ]; then
    echo "📁 Creating bin directory"
    mkdir -p bin
else
    echo "✅ Bin directory already exists"
fi

echo "🎉 Codebase structure setup complete!"
echo ""
echo "Current structure:"
echo "  /code          - Main source code (single source of truth)"
echo "  /app/code      - Symlink to /code (for CI/CD compatibility)"
echo "  /bin           - Archive directory for old files"
echo ""
echo "The codebase now has a single source of truth while maintaining CI/CD compatibility."