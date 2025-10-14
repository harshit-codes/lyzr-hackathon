# API Contracts (Phase 2 - SuperScan focus)

Status: Draft
Scope: SuperScan + Project APIs (Snowflake-first). Deep extraction/embeddings/exporters deferred to SuperKB.

---

## Principles
- Keep it simple and achievable
- Snowflake is the single source of truth (logical isolation by project_id)
- SuperScan does sparse, fast ontology proposals and schema CRUD only
- No entity resolution, embeddings, or datapoint creation here

---

## Authentication (placeholder)
- For hackathon: none or simple token header `Authorization: Bearer <token>`
- Production: OIDC/JWT (out of scope)

---

## Error model
```json
{
  "error": {
    "code": "string",
    "message": "string",
    "details": {},
    "trace_id": "uuid",
    "timestamp": "ISO8601"
  }
}
```

---

## Resources and IDs
- project_id, file_id, schema_id, proposal_id are UUIDs
- All endpoints are versioned under /api/v1/

---

## Project API

Create project
- POST /api/v1/projects
- Body
```json
{
  "project_name": "string",      
  "display_name": "string|null",
  "owner_id": "string",
  "tags": ["string"],
  "config": {
    "default_embedding_model": "text-embedding-3-small",
    "embedding_dimension": 1536,
    "default_chunk_size": 512,
    "chunk_overlap": 50,
    "enable_auto_embedding": true,
    "enable_entity_resolution": true,
    "entity_similarity_threshold": 0.85,
    "llm_model": "gpt-4o",
    "llm_temperature": 0.0
  }
}
```
- 201 Response
```json
{
  "project_id": "uuid",
  "project_name": "string",
  "display_name": "string|null",
  "owner_id": "string",
  "tags": ["string"],
  "status": "active",
  "created_at": "ISO8601"
}
```

Get project
- GET /api/v1/projects/{project_id}
- 200 Response
```json
{
  "project_id": "uuid",
  "project_name": "string",
  "display_name": "string|null",
  "owner_id": "string",
  "tags": ["string"],
  "status": "active|archived|deleted",
  "config": {},
  "stats": {
    "schema_count": 0,
    "node_count": 0,
    "edge_count": 0,
    "document_count": 0,
    "last_updated": "ISO8601|null"
  },
  "created_at": "ISO8601",
  "updated_at": "ISO8601"
}
```

List projects
- GET /api/v1/projects?owner_id=...&limit=20&offset=0
- 200 Response
```json
{
  "items": [ {"project_id": "uuid", "project_name": "string" } ],
  "total": 1
}
```

Update project (partial)
- PATCH /api/v1/projects/{project_id}
- Body
```json
{ "display_name": "string", "tags": ["string"], "config": {"llm_model": "gpt-4o"} }
```
- 200 Response: Project

---

## File Ingestion API (PDF only in Phase 2)

Upload file (PDF)
- POST /api/v1/projects/{project_id}/files
- Content-Type: multipart/form-data
  - file: binary pdf
  - metadata: optional JSON string
- 201 Response
```json
{
  "file_id": "uuid",
  "project_id": "uuid",
  "filename": "Report.pdf",
  "content_type": "application/pdf",
  "size_bytes": 123456,
  "pages": 42,
  "status": "uploaded",
  "created_at": "ISO8601"
}
```

Get file
- GET /api/v1/projects/{project_id}/files/{file_id}
- 200 Response: file record

List files
- GET /api/v1/projects/{project_id}/files
- 200 Response: { items: [...], total: N }

---

## Ontology Proposal API (Sparse Scan)

Trigger sparse scan and proposal
- POST /api/v1/projects/{project_id}/proposals
- Body
```json
{
  "file_ids": ["uuid"],
  "llm": { "model": "gpt-3.5-turbo", "temperature": 0.0 },
  "hints": { "domain": "optional domain string" }
}
```
- 202 Response
```json
{
  "proposal_id": "uuid",
  "status": "processing",
  "estimated_ready_at": "ISO8601"
}
```

Get proposal
- GET /api/v1/projects/{project_id}/proposals/{proposal_id}
- 200 Response (example)
```json
{
  "proposal_id": "uuid",
  "status": "ready|processing|failed",
  "summary": "Short overview",
  "nodes": [
    {
      "schema_name": "Person",
      "entity_type": "NODE",
      "structured_attributes": [
        { "name": "name", "data_type": "string", "required": true },
        { "name": "email", "data_type": "string", "required": false }
      ],
      "notes": "optional free-text"
    }
  ],
  "edges": [
    {
      "schema_name": "WORKS_AT",
      "entity_type": "EDGE",
      "structured_attributes": [
        { "name": "since", "data_type": "integer", "required": false }
      ],
      "direction": "DIRECTED"
    }
  ],
  "source_files": ["uuid"],
  "created_at": "ISO8601"
}
```

Refine proposal (user feedback)
- POST /api/v1/projects/{project_id}/proposals/{proposal_id}/refine
- Body
```json
{
  "add_nodes": [
    { "schema_name": "Organization", "attributes": [ {"name":"name","data_type":"string","required":true} ] }
  ],
  "remove_nodes": ["LegacyType"],
  "mutate_attributes": [
    { "schema_name": "Person", "op": "add", "attribute": {"name":"phone","data_type":"string"} }
  ]
}
```
- 200 Response: updated proposal

Finalize proposal → create schemas
- POST /api/v1/projects/{project_id}/proposals/{proposal_id}/finalize
- 201 Response
```json
{
  "schemas": [ { "schema_id": "uuid", "schema_name": "Person", "version": "1.0.0" } ]
}
```

---

## Schema API (CRUD + Versioning)

Create schema
- POST /api/v1/projects/{project_id}/schemas
- Body
```json
{
  "schema_name": "Person",
  "entity_type": "NODE|EDGE",
  "version": "1.0.0",
  "description": "optional",
  "structured_attributes": [
    { "name": "name", "data_type": "string", "required": true }
  ]
}
```
- 201 Response: schema record

List schemas
- GET /api/v1/projects/{project_id}/schemas
- 200 Response: { items: [...], total: N }

Get schema
- GET /api/v1/projects/{project_id}/schemas/{schema_id}
- 200 Response: schema record

Update schema (minor)
- PATCH /api/v1/projects/{project_id}/schemas/{schema_id}
- Body
```json
{
  "description": "string", 
  "structured_attributes": [ { "name": "email", "data_type": "string" } ]
}
```
- 200 Response: updated schema

Deprecate schema
- POST /api/v1/projects/{project_id}/schemas/{schema_id}/deprecate
- 200 Response: { "schema_id": "uuid", "is_active": false }

---

## Snowflake Storage (SuperScan-only)
- Tables
  - projects (existing Phase 1)
  - schemas (existing Phase 1)
  - files (new; PDF metadata per project)
  - ontology_proposals (new; proposal JSON)
- Write path
  - Use SQLModel + DatabaseConnection context manager
  - Store sparse snippets only (no deep chunks/embeddings)

---

## Non-goals (SuperScan)
- No embeddings/vectorization
- No entity resolution or deduplication
- No graph/vector exports
