# HuggingFace Integration Guide

## Philosophy

**"Don't reinvent the wheel—orchestrate it intelligently."**

We leverage HuggingFace ecosystem for all ML-related tasks to:
- ✅ Focus on unique system architecture
- ✅ Use production-grade, battle-tested components
- ✅ Complete hackathon within timeline
- ✅ Demonstrate intelligent tool selection

---

## Setup

### 1. Get HuggingFace Token
```bash
# Visit: https://huggingface.co/settings/tokens
# Create token with "read" access
# Add to .env:
HUGGINGFACE_TOKEN=hf_xxxxxxxxxxxxxxxxxxxx
```

### 2. Install Dependencies
```bash
pip install sentence-transformers transformers huggingface-hub torch
```

---

## Components Using HuggingFace

### ✅ Phase 1: Chunking (DONE)
**Status**: Simplified to single strategy
- Recursive character splitting
- No complex ML needed for chunking
- Simple, effective, production-ready

### ⬜ Phase 2: Entity Extraction
**HF Component**: NER pipeline
```python
from transformers import pipeline

ner = pipeline("ner", model="dslim/bert-base-NER")
entities = ner(text)
```

### ⬜ Phase 3: Relationship Extraction  
**HF Component**: Zero-shot classification
```python
from transformers import pipeline

classifier = pipeline("zero-shot-classification", 
                     model="facebook/bart-large-mnli")
```

### ⬜ Phase 4: Entity Resolution
**HF Component**: sentence-transformers
```python
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer('all-MiniLM-L6-v2')
similarity = util.cos_sim(emb1, emb2)
```

### ⬜ Phase 5: Embeddings
**HF Component**: sentence-transformers
```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-mpnet-base-v2')
embeddings = model.encode(chunks)
```

### ⬜ Phase 6: Export Services
**Focus**: Neo4j and Pinecone
- Skip AWS Neptune for demo
- Use Pinecone for vector search
- Use Neo4j for graph queries

---

## Benefits

### 1. Faster Development
- No need to implement ML algorithms
- Pre-trained models ready to use
- Focus on integration, not training

### 2. Production Quality
- Models used by thousands of companies
- Well-documented and maintained
- Proven performance

### 3. Hackathon-Friendly
- Complete in 6-day timeline
- Working features, not just prototypes
- Time for unique value proposition

### 4. Evaluation Alignment
Demonstrates:
- ✅ Intelligent tool selection (not reinventing)
- ✅ Production-quality thinking
- ✅ Architectural creativity
- ✅ Focus on unique value (multimodal DB)

---

## Models to Use

### Recommended Models

**NER (Entity Extraction)**:
- `dslim/bert-base-NER` - Fast, general purpose
- `Jean-Baptiste/camembert-ner` - For multilingual
- `allenai/scibert_scivocab_uncased` - For scientific text

**Embeddings**:
- `all-MiniLM-L6-v2` - Fast (384-dim), 80MB
- `all-mpnet-base-v2` - Better quality (768-dim), 420MB  
- `multi-qa-mpnet-base-dot-v1` - For Q&A

**Zero-Shot Classification**:
- `facebook/bart-large-mnli` - General purpose
- `cross-encoder/nli-distilroberta-base` - Faster

---

## Code Examples

### Entity Extraction
```python
from transformers import pipeline
from graph_rag.models.node import Node

# Load NER model
ner = pipeline("ner", model="dslim/bert-base-NER")

# Extract entities
entities = ner(chunk_text)

# Create nodes
for entity in entities:
    node = Node(
        schema_id=schema_id,
        label=entity['entity_group'],
        structured_data={
            "text": entity['word'],
            "confidence": entity['score']
        }
    )
    db.add(node)
```

### Embeddings
```python
from sentence_transformers import SentenceTransformer

# Load model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Generate embeddings
chunks = get_chunks(file_id)
for chunk in chunks:
    embedding = model.encode(chunk.content)
    chunk.embedding = embedding.tolist()
    db.add(chunk)
```

### Entity Resolution
```python
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer('all-MiniLM-L6-v2')

# Compare entities
emb1 = model.encode(entity1_text)
emb2 = model.encode(entity2_text)

similarity = util.cos_sim(emb1, emb2)[0][0]

if similarity > 0.85:  # Threshold
    merge_entities(entity1, entity2)
```

---

## Performance Tips

### 1. Model Caching
```python
import os
os.environ['TRANSFORMERS_CACHE'] = '/path/to/cache'
```

### 2. Batch Processing
```python
# Process in batches for speed
embeddings = model.encode(texts, batch_size=32)
```

### 3. GPU Acceleration
```python
# Use GPU if available
model = SentenceTransformer('model-name', device='cuda')
```

---

## Resources

- **HF Hub Docs**: https://huggingface.co/docs/huggingface_hub/en/index
- **sentence-transformers**: https://www.sbert.net/
- **transformers**: https://huggingface.co/docs/transformers
- **Model Hub**: https://huggingface.co/models

---

## What We're NOT Doing

❌ Training custom models
❌ Fine-tuning (out of hackathon scope)
❌ Complex ensemble methods
❌ Custom NLP algorithms
❌ Reinventing standard ML components

## What We ARE Doing

✅ Intelligent orchestration
✅ Clean integration
✅ Production-quality architecture
✅ Unique multimodal DB design
✅ Agentic retrieval system

---

**Focus**: Build something unique (multimodal database architecture), not something standard (ML models).
