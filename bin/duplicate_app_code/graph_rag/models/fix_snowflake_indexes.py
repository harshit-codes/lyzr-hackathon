#!/usr/bin/env python3
"""
Remove index=True from all SQLModel models for Snowflake compatibility.
Snowflake doesn't support traditional indexes on regular tables.
"""

import re
from pathlib import Path

def remove_indexes(file_path):
    """Remove index=True from a Python file."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Pattern 1: Field(..., index=True, ...)
    content = re.sub(r'(\bField\([^)]*),\s*index=True\s*,', r'\1,', content)
    
    # Pattern 2: Field(..., index=True)
    content = re.sub(r'(\bField\([^)]*),\s*index=True\s*\)', r'\1)', content)
    
    # Pattern 3: Field(index=True, ...)
    content = re.sub(r'(\bField\()\s*index=True\s*,\s*', r'\1', content)
    
    # Pattern 4: Field(index=True)
    content = re.sub(r'\bField\(\s*index=True\s*\)', 'Field()', content)
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"✓ Fixed {file_path.name}")

if __name__ == "__main__":
    models_dir = Path(__file__).parent
    
    for py_file in models_dir.glob("*.py"):
        if py_file.name not in ["__init__.py", "fix_snowflake_indexes.py"]:
            remove_indexes(py_file)
    
    print("\n✅ All models fixed for Snowflake compatibility!")
