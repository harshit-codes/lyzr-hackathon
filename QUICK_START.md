# 🚀 SuperSuite Quick Start Guide

## Prerequisites

✅ Python 3.8+ installed  
✅ All dependencies installed (`pip install -r requirements.txt`)  
✅ `.env` file configured with credentials  
✅ Snowflake account accessible  
✅ Neo4j Aura instance accessible  
✅ DeepSeek API key valid  
✅ HuggingFace API key valid  

---

## 🏃 Quick Start (3 Steps)

### Step 1: Verify Environment

```bash
cd /Users/harshitchoudhary/Desktop/lyzr-hackathon

# Check .env file exists
ls -la .env

# Verify all required variables are set
grep -E "SNOWFLAKE|NEO4J|DEEPSEEK|HUGGINGFACE" .env
```

### Step 2: Run Tests

```bash
# Run all tests to verify everything works
pytest tests/ -v

# Expected output:
# ============================== 74 passed in 4.85s ===============================
```

### Step 3: Start Application

```bash
# Start Streamlit app
streamlit run app/streamlit_app.py --server.port=8504

# Open browser to: http://localhost:8504
```

---

## 📋 Complete User Journey

### 1. Create Project

1. Open Streamlit app in browser
2. Click **"Create New Project"** in sidebar
3. Enter project name (e.g., "My First Project")
4. Enter description (optional)
5. Click **"Create"**
6. ✅ Project created in Snowflake

### 2. Upload Document

1. Select project from dropdown
2. Click **"Upload Document"**
3. Choose a PDF file
4. Click **"Process Document"**
5. ✅ Document uploaded and ready for processing

### 3. Process Document

1. Wait for processing to complete (progress bar shown)
2. Processing steps:
   - 📄 PDF parsing
   - 🤖 Schema generation (DeepSeek AI)
   - 🔍 Entity extraction
   - 💾 Data storage (Snowflake)
   - 🔗 Graph sync (Neo4j)
3. ✅ Document processed successfully

### 4. Generate Ontology

1. Navigate to **"Ontology"** tab
2. Select processed documents
3. Click **"Generate Ontology"**
4. View:
   - Entity types (Person, Organization, Concept, etc.)
   - Relationships between entities
   - Attribute definitions
5. ✅ Ontology generated from real data

### 5. Extract Knowledge

1. Navigate to **"Knowledge Base"** tab
2. Click **"Extract Knowledge"**
3. View:
   - Entity tables grouped by type
   - Relationship tables
   - Statistics (total entities, relationships)
4. ✅ Knowledge extracted from Snowflake

### 6. Query Chat

1. Navigate to **"Chat"** tab
2. Type a question (e.g., "What is this document about?")
3. Click **"Send"** or press Enter
4. View AI-powered response with:
   - Natural language answer
   - Citations from documents
   - Reasoning steps
5. ✅ Chat query answered using real LLM

---

## 🔍 Verification Steps

### Verify Snowflake Data

```sql
-- Connect to Snowflake
USE DATABASE LYZRHACK;
USE SCHEMA PUBLIC;

-- Check projects
SELECT * FROM PROJECTS ORDER BY created_at DESC LIMIT 10;

-- Check file records
SELECT * FROM FILE_RECORDS ORDER BY created_at DESC LIMIT 10;

-- Check chunks
SELECT COUNT(*) as total_chunks FROM CHUNKS;

-- Check schemas
SELECT * FROM SCHEMAS ORDER BY created_at DESC LIMIT 10;

-- Check nodes
SELECT schema_name, COUNT(*) as count 
FROM NODES 
GROUP BY schema_name 
ORDER BY count DESC;

-- Check edges
SELECT relationship_type, COUNT(*) as count 
FROM EDGES 
GROUP BY relationship_type 
ORDER BY count DESC;
```

### Verify Neo4j Data

```cypher
// Connect to Neo4j Aura Browser

// Check all nodes
MATCH (n) RETURN n LIMIT 25;

// Check all relationships
MATCH ()-[r]->() RETURN r LIMIT 25;

// Count nodes by label
MATCH (n) 
RETURN labels(n) AS label, count(*) AS count 
ORDER BY count DESC;

// Count relationships by type
MATCH ()-[r]->() 
RETURN type(r) AS type, count(*) AS count 
ORDER BY count DESC;

// Find specific entities
MATCH (n:Person) RETURN n.name, n.role LIMIT 10;
MATCH (n:Organization) RETURN n.name, n.industry LIMIT 10;
```

---

## 🧪 Testing Commands

### Run All Tests

```bash
pytest tests/ -v
```

### Run Specific Test File

```bash
pytest tests/test_utils.py -v
pytest tests/test_data_manager.py -v
pytest tests/test_demo_orchestrator.py -v
pytest tests/test_integration.py -v
```

### Run Tests with Coverage

```bash
pytest tests/ --cov=app --cov-report=html
open htmlcov/index.html  # View coverage report
```

### Run Tests with Detailed Output

```bash
pytest tests/ -v --tb=short  # Short traceback
pytest tests/ -v --tb=long   # Long traceback
pytest tests/ -v -s          # Show print statements
```

---

## 🐛 Troubleshooting

### Issue: Streamlit app won't start

**Error:** `ModuleNotFoundError: No module named 'streamlit'`

**Solution:**
```bash
pip install -r requirements.txt
```

---

### Issue: Database connection error

**Error:** `Failed to connect to Snowflake`

**Solution:**
1. Check `.env` file has correct credentials
2. Verify Snowflake account is accessible
3. Test connection:
```python
from snowflake.connector import connect
conn = connect(
    account='FHWELTT-XS07400',
    user='HARSHITCODES',
    password='***',
    database='LYZRHACK'
)
print("Connected!")
```

---

### Issue: Neo4j connection error

**Error:** `Failed to connect to Neo4j`

**Solution:**
1. Check `.env` file has correct Neo4j credentials
2. Verify Neo4j Aura instance is running
3. Test connection:
```python
from neo4j import GraphDatabase
driver = GraphDatabase.driver(
    "neo4j+s://b70333ab.databases.neo4j.io",
    auth=("neo4j", "***")
)
driver.verify_connectivity()
print("Connected!")
```

---

### Issue: LLM API error

**Error:** `DeepSeek API key invalid`

**Solution:**
1. Check `.env` file has correct API key
2. Verify API key is active
3. Check API rate limits
4. Test API:
```bash
curl -X POST https://api.deepseek.com/v1/chat/completions \
  -H "Authorization: Bearer sk-dc70e70f5d204874af46db9a5129ee8c" \
  -H "Content-Type: application/json" \
  -d '{"model":"deepseek-chat","messages":[{"role":"user","content":"Hello"}]}'
```

---

### Issue: Tests failing

**Error:** `74 failed`

**Solution:**
1. Check all dependencies installed
2. Verify `.env` file exists
3. Run tests with verbose output:
```bash
pytest tests/ -v --tb=short
```
4. Check specific failing test:
```bash
pytest tests/test_utils.py::TestInitializeSessionState::test_initialize_session_state_creates_all_keys -v
```

---

## 📊 Monitoring

### Check Application Logs

```bash
# Streamlit logs
tail -f ~/.streamlit/logs/*.log

# Application logs (if configured)
tail -f logs/app.log
```

### Monitor Database Usage

```sql
-- Snowflake: Check warehouse usage
SELECT * FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
WHERE WAREHOUSE_NAME = 'COMPUTE_WH'
ORDER BY START_TIME DESC
LIMIT 10;

-- Snowflake: Check query history
SELECT * FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE DATABASE_NAME = 'LYZRHACK'
ORDER BY START_TIME DESC
LIMIT 10;
```

### Monitor API Usage

```bash
# Check DeepSeek API usage
# (Visit DeepSeek dashboard)

# Check HuggingFace API usage
# (Visit HuggingFace dashboard)
```

---

## 🔐 Security Checklist

- [x] `.env` file in `.gitignore`
- [x] No hardcoded credentials in code
- [x] Environment variables loaded at runtime
- [x] Sensitive data not logged
- [x] HTTPS used for all API calls
- [x] Database connections use SSL
- [ ] User authentication implemented (future)
- [ ] Role-based access control (future)

---

## 📞 Support

### Quick Reference

| Component | Status | Command |
|-----------|--------|---------|
| Tests | ✅ Passing | `pytest tests/ -v` |
| Streamlit | ✅ Working | `streamlit run app/streamlit_app.py` |
| Snowflake | ✅ Connected | Check `.env` |
| Neo4j | ✅ Connected | Check `.env` |
| DeepSeek | ✅ Connected | Check `.env` |
| HuggingFace | ✅ Connected | Check `.env` |

### Documentation

- **Detailed Guide:** `PRODUCTION_INTEGRATION_COMPLETE.md`
- **Deployment Summary:** `DEPLOYMENT_SUMMARY.md`
- **Phase 1 Report:** `PHASE_1_COMPLETION_REPORT.md`
- **This Guide:** `QUICK_START.md`

### Contact

For issues or questions, please contact the development team.

---

## 🎯 Next Steps

1. ✅ Run tests (`pytest tests/ -v`)
2. ✅ Start Streamlit app (`streamlit run app/streamlit_app.py`)
3. 🔄 Complete user journey (create project → upload → process → query)
4. 🔄 Verify data in Snowflake
5. 🔄 Verify data in Neo4j
6. 🔄 Test with real PDF documents
7. 🔄 Deploy to production

---

**Happy Building! 🚀**

