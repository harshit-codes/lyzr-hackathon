# Quick Guide: Viewing SuperScan Data in Snowflake

## Access Methods

### Method 1: SQL Worksheets (Recommended) ⭐

**Steps:**
1. Log in to Snowflake Web UI: `https://<your_account>.snowflakecomputing.com`
2. Click **Worksheets** in left navigation
3. Click **+ Worksheet** to create a new worksheet
4. Select warehouse: `COMPUTE_WH` (top right dropdown)
5. Paste and run queries below

**Essential Queries:**

```sql
-- Set context
USE DATABASE superscan;
USE SCHEMA public;

-- View all tables
SHOW TABLES;

-- See row counts
SELECT 
    'projects' as table_name, COUNT(*) as row_count FROM projects
UNION ALL
SELECT 'file_records', COUNT(*) FROM file_records
UNION ALL
SELECT 'ontology_proposals', COUNT(*) FROM ontology_proposals
UNION ALL
SELECT 'schemas', COUNT(*) FROM schemas
UNION ALL
SELECT 'nodes', COUNT(*) FROM nodes
UNION ALL
SELECT 'edges', COUNT(*) FROM edges;
```

---

### Method 2: Data Browser (Visual)

**Steps:**
1. Click **Data** → **Databases** in left navigation
2. Find and expand `SUPERSCAN` database
3. Expand `PUBLIC` schema
4. Click on any table name (e.g., `PROJECTS`, `SCHEMAS`, `NODES`)
5. Click **Data Preview** tab
6. Use **Columns** tab to see structure

---

## View Specific Data

### 1. Projects

```sql
SELECT 
    id,
    name,
    status,
    owner_id,
    config:embedding_model::STRING as embedding_model,
    config:llm_model::STRING as llm_model,
    created_at,
    updated_at
FROM projects
ORDER BY created_at DESC;
```

### 2. File Records

```sql
SELECT 
    id,
    project_id,
    filename,
    file_type,
    size_bytes,
    pages,
    file_metadata,
    upload_status,
    uploaded_at
FROM file_records
ORDER BY uploaded_at DESC;
```

### 3. Ontology Proposals

```sql
SELECT 
    id,
    project_id,
    status,
    summary,
    nodes,
    edges,
    source_files,
    created_at
FROM ontology_proposals
ORDER BY created_at DESC;
```

**Parse proposal nodes/edges:**

```sql
SELECT 
    id,
    project_id,
    summary,
    ARRAY_SIZE(nodes) as node_count,
    ARRAY_SIZE(edges) as edge_count,
    status
FROM ontology_proposals;
```

### 4. Schemas (Finalized Ontology)

```sql
SELECT 
    id,
    project_id,
    schema_name,
    version,
    entity_type,
    is_active,
    structured_attributes,
    created_at
FROM schemas
ORDER BY created_at DESC;
```

**Parse structured attributes:**

```sql
SELECT 
    id,
    schema_name,
    version,
    entity_type,
    structured_attributes[0]:name::STRING as first_attr_name,
    structured_attributes[0]:data_type::STRING as first_attr_type,
    structured_attributes[0]:required::BOOLEAN as first_attr_required
FROM schemas
WHERE entity_type = 'NODE';
```

### 5. Nodes (Graph Data)

```sql
SELECT 
    id,
    schema_id,
    label,
    structured_data,
    unstructured_data,
    node_metadata,
    created_at
FROM nodes
ORDER BY created_at DESC
LIMIT 100;
```

**Parse node data:**

```sql
SELECT 
    id,
    label,
    structured_data:name::STRING as name,
    structured_data:type::STRING as type,
    unstructured_data:description::STRING as description
FROM nodes
LIMIT 50;
```

### 6. Edges (Relationships)

```sql
SELECT 
    id,
    schema_id,
    source_node_id,
    target_node_id,
    label,
    structured_data,
    edge_metadata,
    created_at
FROM edges
ORDER BY created_at DESC
LIMIT 100;
```

**View relationships with node labels:**

```sql
SELECT 
    e.id,
    e.label as relationship_type,
    n1.label as source_label,
    n2.label as target_label,
    e.structured_data,
    e.created_at
FROM edges e
LEFT JOIN nodes n1 ON e.source_node_id = n1.id
LEFT JOIN nodes n2 ON e.target_node_id = n2.id
ORDER BY e.created_at DESC
LIMIT 50;
```

---

## Common VARIANT Data Queries

Snowflake stores JSON-like data in VARIANT columns. Use these patterns to extract data:

### Basic Extraction

```sql
-- Extract string
SELECT config:embedding_model::STRING FROM projects;

-- Extract number
SELECT config:chunk_size::INTEGER FROM projects;

-- Extract boolean
SELECT config:enabled::BOOLEAN FROM projects;

-- Extract array
SELECT config:tags FROM projects;

-- Extract nested object
SELECT config:vector_config:dimensions::INTEGER FROM projects;
```

### Array Operations

```sql
-- Array size
SELECT 
    schema_name,
    ARRAY_SIZE(structured_attributes) as attr_count
FROM schemas;

-- Iterate array elements
SELECT 
    schema_name,
    value:name::STRING as attribute_name,
    value:data_type::STRING as attribute_type
FROM schemas,
LATERAL FLATTEN(input => structured_attributes);

-- Filter array elements
SELECT 
    schema_name,
    structured_attributes
FROM schemas
WHERE ARRAY_CONTAINS('id'::VARIANT, structured_attributes);
```

---

## Debugging Queries

### Check Table Structures

```sql
-- Describe table columns
DESCRIBE TABLE projects;
DESCRIBE TABLE schemas;
DESCRIBE TABLE nodes;
DESCRIBE TABLE edges;
```

### Verify Data Integrity

```sql
-- Check for orphaned nodes (no valid schema)
SELECT 
    n.id,
    n.label,
    n.schema_id
FROM nodes n
LEFT JOIN schemas s ON n.schema_id = s.id
WHERE s.id IS NULL;

-- Check for orphaned edges
SELECT 
    e.id,
    e.label,
    e.source_node_id,
    e.target_node_id
FROM edges e
LEFT JOIN nodes n1 ON e.source_node_id = n1.id
LEFT JOIN nodes n2 ON e.target_node_id = n2.id
WHERE n1.id IS NULL OR n2.id IS NULL;
```

### Performance Queries

```sql
-- Query history (last 10 queries)
SELECT 
    query_id,
    query_text,
    user_name,
    execution_status,
    start_time,
    end_time,
    total_elapsed_time / 1000 as seconds
FROM TABLE(INFORMATION_SCHEMA.QUERY_HISTORY())
ORDER BY start_time DESC
LIMIT 10;

-- Storage usage
SELECT 
    table_name,
    row_count,
    bytes,
    bytes / (1024 * 1024) as mb
FROM information_schema.tables
WHERE table_schema = 'PUBLIC'
    AND table_catalog = 'SUPERSCAN'
ORDER BY bytes DESC;
```

---

## Export Data

### CSV Export

1. Run query in worksheet
2. Click **⬇ Download** button (top right of results)
3. Choose format: CSV, TSV, JSON

### Copy to Clipboard

```sql
SELECT * FROM projects;
-- Click results → Select rows → Right-click → Copy
```

### Export to S3 (Advanced)

```sql
COPY INTO @my_s3_stage/projects.csv
FROM projects
FILE_FORMAT = (TYPE = CSV HEADER = TRUE)
OVERWRITE = TRUE;
```

---

## Tips & Tricks

### 1. Format VARIANT Output

```sql
-- Pretty print JSON
SELECT 
    TO_JSON(structured_data) as formatted_json
FROM nodes
LIMIT 1;
```

### 2. Search Within VARIANT

```sql
-- Find nodes with specific attribute
SELECT *
FROM nodes
WHERE structured_data:name::STRING LIKE '%Research%';
```

### 3. Aggregate VARIANT Data

```sql
-- Count nodes by type
SELECT 
    structured_data:type::STRING as node_type,
    COUNT(*) as count
FROM nodes
GROUP BY node_type
ORDER BY count DESC;
```

### 4. Join on VARIANT Fields

```sql
-- Find edges connecting specific node types
SELECT 
    e.label,
    n1.structured_data:type::STRING as source_type,
    n2.structured_data:type::STRING as target_type,
    COUNT(*) as count
FROM edges e
JOIN nodes n1 ON e.source_node_id = n1.id
JOIN nodes n2 ON e.target_node_id = n2.id
GROUP BY e.label, source_type, target_type;
```

---

## Keyboard Shortcuts

- **Run Query**: `Cmd/Ctrl + Enter`
- **Run Selected**: Select text → `Cmd/Ctrl + Enter`
- **Format SQL**: `Cmd/Ctrl + Shift + F`
- **New Worksheet**: `Cmd/Ctrl + N`
- **Save Worksheet**: `Cmd/Ctrl + S`

---

## Quick Links

- **Worksheets**: `/worksheets`
- **Data Browser**: `/data/databases`
- **Query History**: `/history`
- **Account Settings**: `/account`

---

**Need Help?**
- Check Snowflake docs: https://docs.snowflake.com
- SuperScan PAT auth guide: `notes/decisions/snowflake-pat-authentication-guide.md`
