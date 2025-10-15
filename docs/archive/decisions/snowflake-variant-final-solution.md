# Snowflake VARIANT Type - Final Solution

**Date**: 2025-10-15  
**Status**: ✅ RESOLVED

## Problem

Snowflake connector for Python does NOT support binding Python dict/list types directly. The error encountered was:

```
snowflake.connector.errors.ProgrammingError: 
255001: Binding data in type (dict) is not supported.
```

And when trying to use PARSE_JSON or TO_VARIANT in VALUES clause:

```
002014 (22000): SQL compilation error:
Invalid expression [PARSE_JSON('{}')] in VALUES clause
```

## Root Cause

1. Snowflake connector explicitly does not support dict/list binding
2. VARIANT columns require JSON strings, not Python objects
3. Snowflake SQL does NOT allow expressions (PARSE_JSON, TO_VARIANT, CAST) in INSERT...VALUES clause
4. Must use INSERT...SELECT instead

## Solution

### 1. VariantType Serialization
**File**: `code/graph_rag/db/variant_type.py`

Return JSON strings from `process_bind_param()`:

```python
def process_bind_param(self, value: Any, dialect) -> Any:
    if value is None:
        return None
    
    if hasattr(value, 'model_dump'):
        value = value.model_dump()
    
    # Return JSON string - Snowflake connector requires this
    return json.dumps(value)
```

### 2. SQL Rewriter Event Listener
**File**: `code/graph_rag/db/connection.py`

Rewrite INSERT...VALUES to INSERT...SELECT with PARSE_JSON:

```python
@event.listens_for(self.engine, "before_cursor_execute", retval=True)
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    \"\"\"Rewrite INSERT ... VALUES to INSERT ... SELECT for VARIANT columns.\"\"\"
    if statement.strip().upper().startswith("INSERT") and isinstance(parameters, dict):
        variant_cols = ['config', 'stats', 'tags', 'custom_metadata', 
                       'structured_data', 'unstructured_data', 
                       'properties', 'sample_data']
        
        has_variant = any(col in parameters and isinstance(parameters[col], str) 
                         for col in variant_cols)
        
        if has_variant and " VALUES " in statement.upper():
            # Extract columns
            values_idx = statement.upper().find(" VALUES ")
            insert_part = statement[:values_idx]
            
            cols_start = insert_part.rfind('(')
            cols_end = insert_part.rfind(')')
            cols_str = insert_part[cols_start+1:cols_end]
            cols = [c.strip() for c in cols_str.split(',')]
            
            # Build SELECT with PARSE_JSON for VARIANT columns
            select_items = []
            for col in cols:
                if col in variant_cols and col in parameters:
                    select_items.append(f"PARSE_JSON(%({col})s)")
                else:
                    select_items.append(f"%({col})s")
            
            # Rewrite as INSERT...SELECT
            statement = f"{insert_part} SELECT {', '.join(select_items)}"
    
    return statement, parameters
```

## How It Works

### Before:
```sql
INSERT INTO projects (..., config, ...) 
VALUES (..., '{}', ...)
-- ❌ Snowflake treats '{}' as VARCHAR, not VARIANT
```

### After (Automatic Rewrite):
```sql
INSERT INTO projects (..., config, ...) 
SELECT ..., PARSE_JSON('{}'), ...
-- ✅ PARSE_JSON allowed in SELECT, converts string to VARIANT
```

## Verification

✅ **Test Result**: Project successfully created in Snowflake

```
📋 PHASE 2: Create Project
--------------------------------------------------------------------------------
  ✓ Project Created
    ID: 9976d68d-e799-43ef-8ccc-1bee0c162c2b
    Name: test-resume-knowledge-graph
    Status: active
```

## Key Learnings

1. **Snowflake connector limitations**: No direct dict/list binding support
2. **SQL syntax restrictions**: No expressions in VALUES clause
3. **Workaround pattern**: INSERT...SELECT + PARSE_JSON
4. **Event listeners**: Powerful for SQL rewriting at runtime
5. **Context7 docs**: Essential for understanding vendor-specific quirks

## Files Modified

1. `code/graph_rag/db/variant_type.py` - JSON serialization
2. `code/graph_rag/db/connection.py` - SQL rewriter event listener
3. `code/tests/test_variant_type.py` - Updated test expectations

## Performance Impact

- **Minimal**: INSERT...SELECT is as fast as INSERT...VALUES in Snowflake
- **Single-row inserts**: No noticeable difference
- **Bulk inserts**: Same performance characteristics

## Future Improvements

1. Monitor Snowflake connector updates for native dict/list support
2. Consider caching parsed column lists to avoid regex parsing
3. Add metrics/logging for SQL rewrites if needed

## References

- Snowflake VARIANT docs: https://docs.snowflake.com/en/sql-reference/data-types-semistructured
- Snowflake SQLAlchemy: https://docs.snowflake.com/developer-guide/python-connector/sqlalchemy
- Context7 MCP docs lookup: Successfully used to understand VARIANT handling
