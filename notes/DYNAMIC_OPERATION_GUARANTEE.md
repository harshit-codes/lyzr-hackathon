# SuperScan Dynamic Operation Guarantee

**Date:** October 15, 2025  
**Purpose:** Ensure SuperScan works with ANY document and supports dynamic schema evolution  

---

## 🎯 Core Principles

### 1. **No Hardcoded Schemas**
SuperScan does NOT use predefined entity types or relationships. Everything is discovered from documents using LLM analysis.

### 2. **Content-Adaptive Ontology**
The knowledge graph schema adapts to document content, not the other way around.

### 3. **User-Driven Evolution**
Users control the ontology through natural language feedback and refinement cycles.

---

## ✅ How We Ensure Dynamic Operation

### 1. LLM-Powered Ontology Discovery

**Process:**
```
Document → LLM Analysis → Ontology Proposal → User Review → Finalized Schema
```

**Key Files:**
- `superscan/fast_scan.py` - LLM-based sparse scanning
- `superscan/proposal_service.py` - Proposal generation and refinement
- No hardcoded entity lists

**Code Evidence:**
```python
# FastScan.generate_proposal() uses DeepSeek to discover entities
# NOT a predefined list
def generate_proposal(self, snippets, hints=None):
    """
    Generate ontology from document snippets using LLM.
    NO hardcoded entity types - all discovered from content.
    """
    prompt = self._build_proposal_prompt(snippets, hints)
    response = self.client.chat.completions.create(...)
    # LLM returns discovered entities, not predefined ones
    return self._parse_ontology(response)
```

**Validation:** See `tests/test_dynamic_superscan.py::test_ontology_generation_is_dynamic`

---

### 2. Schema Evolution & Versioning

**User Workflow:**
1. Review proposed schema
2. Request changes via natural language
3. System applies changes + increments version
4. User approves finalized schema

**Semantic Versioning:**
- `v1.0.0` → `v1.1.0`: Added optional attribute (minor change)
- `v1.1.0` → `v2.0.0`: Added required attribute (major/breaking change)

**Key Files:**
- `graph_rag/models/schema.py` - Version field, validation
- `superscan/schema_service.py` - Schema CRUD + versioning
- `superscan/proposal_service.py` - Update and finalize proposals

**Code Evidence:**
```python
# Schema has version field
class Schema(SQLModel, table=True):
    version: str = Field(default="1.0.0", max_length=20)
    is_active: bool = Field(default=True)  # Support multiple versions
    
    @field_validator('version')
    def validate_version(cls, v: str) -> str:
        # Enforces semantic versioning: major.minor.patch
        parts = v.split('.')
        if len(parts) != 3:
            raise ValueError("Must follow semantic versioning")
        return v
```

**Validation:** See `tests/test_dynamic_superscan.py::test_schema_evolution_user_updates`

---

### 3. Backwards Compatibility

**Rules:**
- ✅ Adding optional attributes → Minor version bump (v1.0 → v1.1)
- ✅ Old nodes remain valid
- ❌ Adding required attributes → Major version bump (v1.x → v2.0)
- ❌ Requires data migration

**Implementation:**
```python
# Node references schema version
class Node(SQLModel, table=True):
    schema_id: UUID  # Points to specific schema version
    
# Multiple schema versions can coexist
# Old nodes use v1.0, new nodes use v1.1
```

**Validation:** See `tests/test_dynamic_superscan.py::test_schema_backwards_compatibility`

---

### 4. Multi-Document Ontology Extension

**Scenario:** User uploads multiple PDFs with different content types

**Process:**
1. PDF #1 (Resume) → Discovers: Person, Company, Skill
2. PDF #2 (Research Paper) → Discovers: Author, Paper, University
3. System EXTENDS ontology (not replaces)
4. Recognizes similar entities: Person ≈ Author

**Entity Resolution:**
- Fuzzy matching for similar entities
- Confidence scores for merges
- User can approve/reject merges

**Key Files:**
- `superscan/entity_resolution.py` - Entity matching logic
- Fuzzy string matching for names
- Embedding similarity for semantic matching

**Validation:** See `tests/test_dynamic_superscan.py::test_multiple_pdfs_extend_ontology`

---

### 5. User Control & Approval

**Important:** SuperScan NEVER auto-applies schemas

**Workflow:**
```
1. Generate Proposal (status: "proposed", finalized: False)
2. User Reviews → Can modify
3. User Approves → finalize_proposal()
4. Schemas Created (status: "finalized")
```

**Code Evidence:**
```python
# Proposal has explicit finalization
class Proposal:
    status: str  # "proposed" | "modified" | "finalized"
    finalized: bool = False
    
def finalize_proposal(proposal_id):
    # Only creates schemas when user explicitly approves
    if proposal.status != "finalized":
        # Create versioned schemas
        # Save to database
        proposal.finalized = True
```

**Validation:** See `tests/test_dynamic_superscan.py::test_schema_suggestion_not_user_confirmation`

---

## 🧪 Test Coverage

### Dynamic Operation Tests

| Test | Purpose | Status |
|------|---------|--------|
| `test_ontology_generation_is_dynamic` | Ensures NO hardcoded schemas | ✅ |
| `test_schema_evolution_user_updates` | Validates versioning & updates | ✅ |
| `test_schema_backwards_compatibility` | Ensures old data remains valid | ✅ |
| `test_multiple_pdfs_extend_ontology` | Tests multi-doc schema growth | ✅ |
| `test_real_llm_extraction_not_mocked` | Validates real API calls | ✅ |
| `test_entity_resolution_across_documents` | Tests deduplication | ✅ |
| `test_schema_suggestion_not_user_confirmation` | User approval required | ✅ |

**Run tests:**
```bash
cd code
pytest tests/test_dynamic_superscan.py -v
```

---

## 📋 Real-World Example

### Scenario: Resume Processing

**Input:** `resume-harshit.pdf` (real PDF, not mocked)

**Step 1: LLM discovers ontology**
```json
{
  "nodes": [
    {"schema_name": "Person", "attributes": ["name", "role"]},
    {"schema_name": "Company", "attributes": ["name", "industry"]},
    {"schema_name": "Skill", "attributes": ["name", "category"]}
  ],
  "edges": [
    {"schema_name": "WORKS_AT", "from": "Person", "to": "Company"},
    {"schema_name": "HAS_SKILL", "from": "Person", "to": "Skill"}
  ]
}
```

**Step 2: User feedback**
> "Add 'certifications' to Person and create EARNED_CERTIFICATION edge"

**Step 3: System applies changes**
```json
{
  "nodes": [
    {
      "schema_name": "Person",
      "version": "1.1.0",  // ← Incremented
      "attributes": ["name", "role", "certifications"]  // ← Added
    },
    {"schema_name": "Certification", "attributes": ["name", "issuer"]}  // ← New
  ],
  "edges": [
    {"schema_name": "WORKS_AT", ...},
    {"schema_name": "HAS_SKILL", ...},
    {"schema_name": "EARNED_CERTIFICATION", "from": "Person", "to": "Certification"}  // ← New
  ]
}
```

**Step 4: User approves**
- Schemas v1.1.0 created in database
- Ready for entity extraction

**See:** `code/notebooks/test_superscan_flow.py` (lines 225-374)

---

## 🔄 Schema Evolution Example

### Before (v1.0.0)
```json
{
  "schema_name": "Person",
  "version": "1.0.0",
  "attributes": [
    {"name": "name", "required": true},
    {"name": "age", "required": false}
  ]
}
```

### After User Request: "Add email and phone"
```json
{
  "schema_name": "Person",
  "version": "1.1.0",  // ← Minor version bump (compatible)
  "attributes": [
    {"name": "name", "required": true},
    {"name": "age", "required": false},
    {"name": "email", "required": false},  // ← New optional
    {"name": "phone", "required": false}   // ← New optional
  ]
}
```

**Result:** Old nodes (v1.0.0) still valid! New nodes can use v1.1.0.

---

## 🚫 What We DON'T Do

### ❌ Hardcoded Entity Types
```python
# WRONG - This is NOT in our code
PREDEFINED_ENTITIES = ["Person", "Company", "Product"]  # ❌ NO!
```

### ❌ Fixed Relationship Types
```python
# WRONG - This is NOT in our code
ALLOWED_RELATIONSHIPS = ["WORKS_AT", "OWNS", "MANAGES"]  # ❌ NO!
```

### ❌ Auto-Apply Schemas
```python
# WRONG - We don't do this
schema = generate_proposal(doc)
schema_service.create_schema(schema)  # ❌ No user approval!
```

---

## ✅ What We DO

### ✅ LLM-Discovered Entities
```python
# Correct - Entities discovered from content
proposal = fast_scan.generate_proposal(text_snippets)
# Returns whatever LLM finds in the document
```

### ✅ User-Approved Schemas
```python
# Correct - User must approve
proposal = proposal_service.create_proposal(...)  # status="proposed"
# User reviews and modifies
updated = proposal_service.update_proposal(...)
# Only create after approval
finalized = proposal_service.finalize_proposal(proposal_id)
```

### ✅ Versioned Evolution
```python
# Correct - Schemas are versioned
schema_v1 = Schema(schema_name="Person", version="1.0.0", ...)
schema_v2 = Schema(schema_name="Person", version="1.1.0", ...)
# Both can coexist, nodes reference specific version
```

---

## 📊 Evidence in Codebase

### File: `superscan/fast_scan.py`
**Lines 45-120:** LLM-based ontology generation (no hardcoded entities)

### File: `superscan/proposal_service.py`
**Lines 30-85:** Proposal creation with "proposed" status  
**Lines 150-210:** User modification support  
**Lines 250-320:** Explicit finalization required  

### File: `graph_rag/models/schema.py`
**Lines 60-70:** Version field with semantic versioning  
**Lines 134-162:** Version validation logic  

### File: `notebooks/test_superscan_flow.py`
**Lines 140-165:** Real PDF → LLM ontology discovery  
**Lines 225-374:** User feedback → Schema refinement  
**Lines 380-398:** Explicit user approval step  

---

## 🎓 Summary

### SuperScan Guarantees:

1. ✅ **NO hardcoded schemas** - All discovered via LLM
2. ✅ **Works with ANY PDF** - Content-adaptive ontology
3. ✅ **User-driven evolution** - Natural language refinement
4. ✅ **Semantic versioning** - Backwards compatibility
5. ✅ **Multi-document extension** - Ontology grows with corpus
6. ✅ **Explicit approval** - No auto-application
7. ✅ **Entity resolution** - Deduplication across documents

### Test Evidence:

- **7 dynamic operation tests** (see `tests/test_dynamic_superscan.py`)
- **Real LLM integration** (DeepSeek API for extraction)
- **Real PDF processing** (see `notebooks/test_superscan_flow.py`)
- **Schema evolution flow** (proposal → review → modify → approve)

---

## 🔍 How to Verify

### 1. Run Dynamic Tests
```bash
cd code
export DEEPSEEK_API_KEY="your_key"
export OPENAI_API_KEY="your_key"
pytest tests/test_dynamic_superscan.py -v
```

### 2. Run End-to-End Test
```bash
cd code
python notebooks/test_superscan_flow.py
# Watch it discover schemas from real PDF
# Watch user refinement cycle
# Watch versioning in action
```

### 3. Try Different PDF
```bash
# Replace resume with ANY other PDF
cp /path/to/your/document.pdf notebooks/test_data/test.pdf
# Update test_superscan_flow.py line 109 to use test.pdf
python notebooks/test_superscan_flow.py
# Will discover DIFFERENT ontology based on content
```

---

**Document Version:** 1.0  
**Last Updated:** October 15, 2025  
**Status:** ✅ Verified and Tested
