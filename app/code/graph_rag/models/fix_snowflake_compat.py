#!/usr/bin/env python3
"""
Fix SQLModel models for Snowflake compatibility:
1. Remove index=True (Snowflake doesn't support indexes on regular tables)
2. Replace JSON with VARIANT type
"""

import re
from pathlib import Path

def fix_model_file(file_path):
    """Fix a model file for Snowflake compatibility."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Fix 1: Remove index=True
    content = re.sub(r',\s*index=True', '', content)
    content = re.sub(r'index=True\s*,\s*', '', content)
    content = re.sub(r'Field\(\s*index=True\s*\)', 'Field()', content)
    
    # Fix 2: Replace JSON import
    content = re.sub(
        r'from sqlmodel import (.*?)JSON,\s*(.*)',
        r'from sqlmodel import \1\2',
        content
    )
    content = re.sub(
        r'from sqlmodel import (.*?),\s*JSON(.*)',
        r'from sqlmodel import \1\2',
        content
    )
    
    # Fix 3: Add VARIANT import from snowflake.sqlalchemy
    if 'Column(JSON)' in content and 'from snowflake.sqlalchemy import VARIANT' not in content:
        # Find the last import line
        import_lines = [i for i, line in enumerate(content.split('\n')) if line.strip().startswith('from ') or line.strip().startswith('import ')]
        if import_lines:
            lines = content.split('\n')
            last_import_idx = import_lines[-1]
            lines.insert(last_import_idx + 1, 'from snowflake.sqlalchemy import VARIANT')
            content = '\n'.join(lines)
    
    # Fix 4: Replace Column(JSON) with Column(VARIANT)
    content = re.sub(r'Column\(JSON\)', 'Column(VARIANT)', content)
    
    if content != original_content:
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"✓ Fixed {file_path.name}")
        return True
    else:
        print(f"  {file_path.name} (no changes)")
        return False

if __name__ == "__main__":
    models_dir = Path(__file__).parent
    
    fixed_count = 0
    for py_file in models_dir.glob("*.py"):
        if py_file.name not in ["__init__.py", "fix_snowflake_compat.py", "fix_snowflake_indexes.py"]:
            if fix_model_file(py_file):
                fixed_count += 1
    
    print(f"\n✅ Fixed {fixed_count} model(s) for Snowflake compatibility!")
