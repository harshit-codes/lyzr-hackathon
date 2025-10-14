# Code Directory

## Structure

```
code/
├── notebooks/          # Rapid prototyping notebooks
│   └── prototype_v1.ipynb  # Initial end-to-end implementation
└── src/               # Production code (will be populated after notebook validation)
    ├── models/        # Data models (Schema, Node, Edge)
    ├── database/      # Snowflake and export connectors
    ├── processing/    # Document processing pipeline
    ├── retrieval/     # Retrieval orchestrator
    └── ui/            # Streamlit components
```

## Development Approach

### Phase 0: Notebook-First Prototyping (Current)
1. Build complete functionality in `notebooks/prototype_v1.ipynb`
2. Test all components:
   - Data models with Pydantic
   - Snowflake integration
   - Document processing
   - Export scripts (Neo4j, Pinecone, PostgreSQL)
   - Retrieval orchestrator
3. Host notebook in Streamlit for immediate testing
4. Validate architecture decisions

### Phase 1+: Production Refactoring
Once notebook is validated:
1. Refactor into proper Python modules in `src/`
2. Create clean class hierarchies
3. Add comprehensive error handling
4. Implement logging and monitoring
5. Write unit and integration tests
6. Build production Streamlit UI

## Getting Started

### Prerequisites
```bash
pip install pydantic pandas numpy jupyter
```

### Run Prototype Notebook
```bash
jupyter notebook notebooks/prototype_v1.ipynb
```

## Current Status
- ✅ Data models defined (Schema, Node, Edge)
- ✅ Schema versioning support
- ✅ Complete content vectorization strategy
- ⏳ Snowflake integration (TODO)
- ⏳ Document processing (TODO)
- ⏳ Export scripts (TODO)
- ⏳ Retrieval orchestrator (TODO)

## Next Steps
1. Set up Snowflake connection
2. Implement CRUD operations for entities
3. Add document processing pipeline
4. Integrate OpenAI for embeddings
5. Build export scripts
6. Create retrieval orchestrator
