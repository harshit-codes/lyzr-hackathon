# Nomenclature Analysis - Lyzr Hackathon

**Date**: 2025-10-14  
**Status**: DRAFT - Analysis Phase

## Overview

This document analyzes the current nomenclature patterns in the codebase and proposes a standardized naming convention for production-quality documentation and maintenance.

## Current Patterns Detected

### ✅ Strong Conventions (Maintain)

1. **Class Names**: `PascalCase`
   - Examples: `Project`, `Schema`, `Node`, `Edge`, `DatabaseConnection`, `StructuredDataValidator`
   - Rationale: Standard Python convention for classes

2. **Functions/Methods**: `snake_case`
   - Examples: `validate_schema_definition()`, `get_session()`, `update_vector()`, `is_active()`
   - Rationale: PEP 8 compliance

3. **Database Fields**: `snake_case`
   - Examples: `project_id`, `schema_id`, `node_id`, `created_at`, `updated_at`
   - Rationale: SQL/Snowflake conventions and SQLModel compatibility

4. **Enums**: `PascalCase` for class, `UPPER_CASE` for values
   - Examples: `ProjectStatus.ACTIVE`, `EdgeDirection.DIRECTED`, `EntityType.NODE`
   - Rationale: Standard enum conventions

5. **Method Prefixes**: Consistent predicate patterns
   - `is_*`: Boolean predicates (`is_active()`, `is_archived()`, `is_self_loop()`)
   - `get_*`: Getters (`get_attribute()`, `get_blob_by_id()`, `get_session()`)
   - `validate_*`: Validators (`validate_schema_name()`, `validate_version()`)
   - `update_*`: Mutators (`update_stats()`, `update_vector()`)

6. **Reserved Word Avoidance**:
   - ✅ `node_metadata` instead of `metadata` (SQLAlchemy reserved)
   - ✅ `custom_metadata` for user-defined fields
   - ✅ `edge_metadata` for relationship metadata

### 🔧 Areas for Standardization

1. **Relationship Type Naming**:
   - **Current**: `relationship_type` field with `UPPER_CASE` values
   - Examples: `WORKS_AT`, `KNOWS`, `MANAGES`, `AUTHORED`
   - **Rationale**: Matches Neo4j/Cypher conventions; improves query readability
   - **Validator**: `validate_relationship_type()` enforces uppercase

2. **Multimodal Data Fields**:
   - ✅ `structured_data`: Dict[str, Any] - validated key-value attributes
   - ✅ `unstructured_data`: List[UnstructuredBlob] - text content with chunks
   - ✅ `vector`: Optional[List[float]] - embeddings
   - **Rationale**: Clear semantic separation for multimodal architecture

3. **ID Suffixes**:
   - ✅ Consistent `*_id` pattern: `project_id`, `schema_id`, `node_id`, `edge_id`
   - ✅ UUID type for all primary keys
   - **Rationale**: Foreign key relationships are immediately identifiable

4. **Timestamp Fields**:
   - ✅ `created_at`, `updated_at`, `deleted_at`, `archived_at`
   - ❌ AVOID: `ts`, `timestamp`, `date` (ambiguous)
   - **Rationale**: Explicit temporal semantics; sortable; standard convention

5. **Configuration Naming**:
   - ✅ `default_*` prefix for defaults: `default_embedding_model`, `default_chunk_size`
   - ✅ `enable_*` prefix for booleans: `enable_auto_embedding`, `enable_entity_resolution`
   - ✅ `*_threshold` suffix for limits: `entity_similarity_threshold`
   - **Rationale**: Self-documenting; reduces need for inline comments

## Nomenclature Style Guide

### 1. Case Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Classes | PascalCase | `Project`, `Node`, `StructuredDataValidator` |
| Functions/Methods | snake_case | `validate_schema()`, `get_session()` |
| Variables | snake_case | `project_id`, `schema_name`, `chunk_size` |
| Constants | UPPER_SNAKE_CASE | `MAX_RETRIES`, `DEFAULT_DIMENSION` |
| Enums | PascalCase (class), UPPER_CASE (values) | `ProjectStatus.ACTIVE` |
| Database Fields | snake_case | `created_at`, `node_metadata` |
| Relationship Types | UPPER_CASE | `WORKS_AT`, `AUTHORED` |

### 2. Method Prefixes

| Prefix | Purpose | Return Type | Example |
|--------|---------|-------------|---------|
| `is_*` | Boolean predicate | bool | `is_active()`, `is_compatible_with()` |
| `has_*` | Existence check | bool | `has_vector`, `has_metadata` |
| `get_*` | Accessor/retrieval | T | `get_attribute()`, `get_session()` |
| `set_*` | Mutator (single field) | None | `set_structured_attribute()` |
| `update_*` | Mutator (multiple fields) | None | `update_stats()`, `update_vector()` |
| `add_*` | Collection append | None | `add_tag()`, `add_blob()` |
| `remove_*` | Collection delete | bool | `remove_tag()`, `remove_blob()` |
| `create_*` | Factory/constructor | T | `create_engine()` |
| `validate_*` | Validation | Tuple[bool, str] | `validate_schema_name()` |

### 3. Reserved Words & Conflicts

**SQLAlchemy Reserved Words** (use prefixed versions):
- ❌ `metadata` → ✅ `node_metadata`, `edge_metadata`, `custom_metadata`
- ❌ `type` (in some contexts) → ✅ `entity_type`, `relationship_type`
- ❌ `session` (class attribute) → ✅ Use local variables only

**Python Reserved Words**:
- Avoid: `class`, `def`, `import`, `from`, `lambda`, `yield`

### 4. Multimodal Data Terminology

| Term | Definition | Field Name |
|------|------------|------------|
| **Structured Data** | Schema-validated key-value attributes | `structured_data` |
| **Unstructured Data** | Text blobs with chunk metadata | `unstructured_data` |
| **Vector** | Embedding array for semantic search | `vector` |
| **Embedding Model** | Model used to generate vectors | `vector_model` |
| **Chunk** | Text segment with offsets | `chunks` (in UnstructuredBlob) |
| **Blob** | Single unstructured content unit | `UnstructuredBlob` |

### 5. Schema & Versioning Terms

| Term | Convention | Example |
|------|-----------|---------|
| Schema Name | PascalCase or UPPER_CASE | `Person`, `AUTHORED` |
| Version | Semantic (major.minor.patch) | `1.0.0`, `2.1.3` |
| Active Flag | `is_active` | `schema.is_active = True` |
| Attribute Name | snake_case | `email`, `full_name`, `created_at` |

### 6. Abbreviations

**Allowed**:
- `id` (identifier)
- `config` (configuration)
- `stats` (statistics)
- `metadata` (with prefix)
- `attr` (attribute, in local scope only)
- `db` (database)
- `uuid` (Universally Unique Identifier)

**Disallowed**:
- `ts` (use `created_at`, `updated_at`)
- `idx` (use `index` or `id`)
- `cnt` (use `count`)
- `str` (use `string` or full variable name)
- `obj` (use descriptive name)

### 7. Foreign Key Naming

Pattern: `{referenced_table}_id`

Examples:
- `project_id` → references `projects.project_id`
- `schema_id` → references `schemas.schema_id`
- `start_node_id` → references `nodes.node_id`
- `end_node_id` → references `nodes.node_id`

**Rationale**: Immediate identification of relationships; self-documenting; supports automated FK detection

### 8. Configuration Parameters

**Patterns**:
- Defaults: `default_{param}` (e.g., `default_embedding_model`)
- Booleans: `enable_{feature}` (e.g., `enable_auto_embedding`)
- Thresholds: `{metric}_threshold` (e.g., `similarity_threshold`)
- Limits: `max_{resource}` (e.g., `max_retries`)
- Sizes: `{entity}_size` (e.g., `chunk_size`, `pool_size`)

## Design Decisions & Rationale

### Why `structured_data` and `unstructured_data`?

**Decision**: Use explicit terminology for multimodal data split

**Why**:
- **Clarity**: Immediately identifies data type at schema level
- **Multimodal Architecture**: Separates schema-validated fields from free-text content
- **Export Compatibility**: Maps cleanly to relational (structured → columns), graph (both → properties), vector (unstructured → embeddings)
- **Educational Value**: Teaches developers the multimodal pattern

**Alternatives Rejected**:
- `properties` (too generic, conflicts with graph DB terminology)
- `attributes` (ambiguous, could mean any field)
- `data` (too vague)

### Why `relationship_type` in UPPER_CASE?

**Decision**: Enforce uppercase for relationship type values

**Why**:
- **Graph DB Conventions**: Matches Neo4j, Cypher, and property graph standards
- **Visual Distinction**: Stands out in queries and logs
- **Query Parity**: When exporting to Neo4j, relationship types will be consistent
- **Code Generation**: Simplifies Cypher query generation

**Example**:
```python
# Python code
edge = Edge(relationship_type="WORKS_AT", ...)

# Exported to Neo4j Cypher
CREATE (a:Person)-[:WORKS_AT]->(b:Company)
```

### Why `node_metadata` instead of `metadata`?

**Decision**: Prefix metadata fields to avoid SQLAlchemy reserved word

**Why**:
- **SQLAlchemy Conflict**: `metadata` is reserved by SQLAlchemy for schema metadata
- **Semantic Clarity**: `node_metadata` explicitly indicates it's node-specific
- **Consistency**: Matches pattern with `edge_metadata`, `custom_metadata`
- **Safety**: Prevents runtime errors and import conflicts

### Why `*_id` suffix for all identifiers?

**Decision**: Use consistent `_id` suffix for all foreign keys and primary keys

**Why**:
- **Self-Documenting**: Field name immediately indicates it's an identifier
- **Grep-Friendly**: Easy to search for all ID fields (`grep "_id"`)
- **Foreign Key Discovery**: Automated tools can detect relationships
- **Type Hints**: Encourages UUID type hints for type safety

### Why `created_at` / `updated_at` instead of `ts`?

**Decision**: Use explicit timestamp field names

**Why**:
- **Semantic Clarity**: `created_at` is unambiguous; `ts` could mean anything
- **Sorting**: `_at` suffix groups related timestamp fields
- **SQL Standards**: Matches common database conventions
- **International**: Clear even for non-native English speakers

## Validation & Enforcement

### Implemented Validators

1. **Field Validators** (Pydantic):
   ```python
   @field_validator('project_name')
   def validate_project_name(cls, v: str) -> str:
       # Enforce snake_case, alphanumeric
   
   @field_validator('relationship_type')
   def validate_relationship_type(cls, v: str) -> str:
       # Enforce UPPER_CASE
   ```

2. **Schema Validators**:
   - `StructuredDataValidator.validate_schema_definition()`
   - Type checking, constraint validation

### Recommended Linters

1. **ruff** with pep8-naming:
   ```toml
   [tool.ruff.lint]
   select = ["N"]  # pep8-naming rules
   ```

2. **mypy** for type safety:
   ```toml
   [tool.mypy]
   strict = true
   warn_unused_configs = true
   ```

3. **pre-commit hooks**:
   - Run linters on staged files
   - Enforce naming conventions before commit

## Migration Strategy

### Phase 1: Documentation (Current)
✅ Document current patterns  
✅ Define style guide  
✅ Create nomenclature reference  

### Phase 2: Validation (Optional)
⏳ Add linter configurations  
⏳ Set up pre-commit hooks  
⏳ CI/CD integration  

### Phase 3: Refactoring (If Needed)
⏳ Identify non-conforming identifiers  
⏳ AST-based codemods  
⏳ Update tests and documentation  
⏳ Database migrations (if field names change)  

## References

- PEP 8: https://peps.python.org/pep-0008/
- SQLAlchemy Naming Conventions: https://docs.sqlalchemy.org/en/20/core/metadata.html
- Neo4j Naming Conventions: https://neo4j.com/docs/cypher-manual/current/syntax/naming/
- Apache AGE Documentation: https://age.apache.org/

---

**Status**: ✅ Ready for documentation generation  
**Next Steps**: Use this guide to populate GitBook Appendix/Nomenclature section
