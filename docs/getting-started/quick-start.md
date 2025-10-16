# Quick Start Guide

Get SuperSuite up and running in 5 minutes! This guide will walk you through starting the application and processing your first document.

---

## Prerequisites

Before you begin, ensure you have completed:

✅ **[Installation](installation.md)** - Python 3.10+, dependencies installed  
✅ **[Configuration](configuration.md)** - `.env` file created with all credentials

---

## Step 1: Activate Virtual Environment

If you created a virtual environment during installation:

```bash
# Navigate to repository
cd /Users/harshitchoudhary/Desktop/lyzr-hackathon

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

**Expected:** Your terminal prompt shows `(venv)` prefix.

---

## Step 2: Verify Configuration

Quick check that environment variables are loaded:

```bash
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('✅ Snowflake:', os.getenv('SNOWFLAKE_ACCOUNT')[:10] + '...'); print('✅ Neo4j:', os.getenv('NEO4J_URI')[:20] + '...'); print('✅ DeepSeek:', 'Configured' if os.getenv('DEEPSEEK_API_KEY') else 'Missing')"
```

**Expected output:**
```
✅ Snowflake: FHWELTT-XS...
✅ Neo4j: neo4j+s://b70333ab...
✅ DeepSeek: Configured
```

---

## Step 3: Start the Application

Launch the Streamlit application:

```bash
streamlit run app/streamlit_app.py --server.port=8504
```

**Expected output:**
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8504
  Network URL: http://192.168.x.x:8504
```

💡 **Tip:** The application will automatically open in your default browser. If not, manually navigate to `http://localhost:8504`.

---

## Step 4: Create Your First Project

### In the Streamlit Interface:

1. **Look at the sidebar** on the left
2. **Find "Create New Project"** section
3. **Enter project details:**
   - **Project Name:** `My First Project`
   - **Description:** `Testing SuperSuite document processing`
4. **Click "Create"** button

**Expected:** Success message appears, and your project is now selectable in the dropdown.

📸 **What you should see:**
- Sidebar with project creation form
- Success notification
- Project appears in "Select Project" dropdown

---

## Step 5: Upload a Document

### In the Streamlit Interface:

1. **Select your project** from the dropdown
2. **Navigate to "Upload Document"** section
3. **Click "Browse files"** button
4. **Select a PDF file** (try `app/notebooks/test_data/resume-harshit.pdf` for testing)
5. **Wait for upload confirmation**

**Expected:** File name and size displayed, ready for processing.

📸 **What you should see:**
- File upload widget
- Uploaded file name
- File size information
- "Process Document" button enabled

---

## Step 6: Process the Document

### In the Streamlit Interface:

1. **Click "Process Document"** button
2. **Wait for processing** (this may take 2-5 minutes)
   - PDF text extraction
   - AI schema generation
   - Entity extraction
   - Database storage
   - Neo4j sync

**Expected:** Progress indicators, then success message.

📸 **What you should see:**
- Processing status messages
- Progress bar or spinner
- Success notification when complete
- Summary of extracted entities

⏱️ **Processing Time:** 2-5 minutes depending on document size and complexity.

---

## Step 7: Explore the Results

### View Ontology (Schema)

1. **Navigate to "Ontology" tab** (or similar)
2. **View entity types** extracted from your document
3. **See relationships** between entities

**Expected:** Table or visualization showing entity types like Person, Organization, Skill, etc.

### View Knowledge Base

1. **Navigate to "Knowledge Base" tab** (or similar)
2. **Browse extracted entities**
3. **View entity properties**

**Expected:** Tables showing actual entities extracted from your document.

### Query with Chat

1. **Navigate to "Chat" tab** (or similar)
2. **Ask a question** about your document
   - Example: "What are the main topics in this document?"
   - Example: "List all the people mentioned"
3. **Receive AI-powered answer**

**Expected:** Relevant answer based on your document content.

---

## Verify Data in Databases

### Check Snowflake (Optional)

If you have access to Snowflake console:

```sql
USE DATABASE LYZRHACK;
USE SCHEMA PUBLIC;

-- View projects
SELECT * FROM PROJECTS ORDER BY created_at DESC LIMIT 5;

-- View files
SELECT * FROM FILE_RECORDS ORDER BY created_at DESC LIMIT 5;

-- View extracted entities
SELECT * FROM NODES LIMIT 10;

-- View relationships
SELECT * FROM EDGES LIMIT 10;
```

### Check Neo4j (Optional)

If you have access to Neo4j Browser:

```cypher
// View all nodes
MATCH (n) RETURN n LIMIT 25;

// View all relationships
MATCH (a)-[r]->(b) RETURN a, r, b LIMIT 25;

// Count nodes by type
MATCH (n) RETURN labels(n) AS type, count(*) AS count ORDER BY count DESC;
```

---

## Troubleshooting Quick Start

### Issue: Application won't start

**Error:** `Port 8504 is already in use`

**Solution:**
```bash
# Kill existing process
lsof -ti:8504 | xargs kill -9

# Or use a different port
streamlit run app/streamlit_app.py --server.port=8505
```

### Issue: Environment variables not found

**Error:** `KeyError: 'SNOWFLAKE_ACCOUNT'`

**Solution:**
```bash
# Verify .env file exists
ls -la .env

# Check contents (be careful not to expose secrets)
head -n 5 .env

# Ensure python-dotenv is installed
pip install python-dotenv
```

### Issue: Database connection fails

**Error:** `Could not connect to Snowflake` or `Neo4j connection failed`

**Solution:**
1. Verify credentials in `.env` file
2. Check network connectivity
3. Ensure databases are running
4. See [Troubleshooting Guide](../reference/troubleshooting.md)

### Issue: Document processing fails

**Error:** `Failed to process document` or `LLM API error`

**Solution:**
1. Verify DeepSeek API key is valid
2. Check API credits/quota
3. Ensure document is a valid PDF
4. Try a smaller document first

### Issue: No entities extracted

**Symptom:** Processing completes but no entities shown

**Solution:**
1. Check document has extractable text (not scanned images)
2. Verify LLM API is working
3. Check Snowflake tables for data
4. Review application logs

---

## Next Steps

🎉 **Congratulations!** You've successfully:
- ✅ Started SuperSuite
- ✅ Created a project
- ✅ Uploaded a document
- ✅ Processed it with AI
- ✅ Explored the results

### Learn More

Now that you're up and running, explore these guides:

1. **[User Guide](../user-guide/overview.md)** - Detailed walkthrough of all features
2. **[Creating Projects](../user-guide/creating-projects.md)** - Project management best practices
3. **[Processing Documents](../user-guide/processing-documents.md)** - Advanced document processing
4. **[Querying with Chat](../user-guide/querying-chat.md)** - Get the most from the chat interface

### Advanced Topics

- **[Architecture](../technical-documentation/architecture.md)** - How SuperSuite works
- **[Database Schema](../technical-documentation/database-schema.md)** - Understanding the data model
- **[API Integrations](../technical-documentation/api-integrations.md)** - DeepSeek and HuggingFace details
- **[Deployment](../technical-documentation/deployment.md)** - Production deployment

---

## Common Workflows

### Workflow 1: Analyze Multiple Documents

1. Create a project for your document collection
2. Upload documents one by one
3. Process each document
4. Use chat to query across all documents

### Workflow 2: Build a Knowledge Base

1. Create a project for your domain (e.g., "Company Policies")
2. Upload all relevant documents
3. Process documents to extract entities
4. Explore the knowledge graph in Neo4j
5. Query with natural language

### Workflow 3: Extract Structured Data

1. Create a project
2. Upload documents with structured information
3. Review generated ontology
4. Export entities from Snowflake for analysis
5. Use in downstream applications

---

## Tips for Success

💡 **Start Small:** Begin with a single, well-structured document to understand the workflow.

💡 **Check Results:** After processing, always verify entities were extracted correctly.

💡 **Use Chat:** The chat interface is powerful - ask specific questions to test understanding.

💡 **Monitor Databases:** Periodically check Snowflake and Neo4j to understand data storage.

💡 **Read Logs:** If something goes wrong, check the Streamlit console output for errors.

---

## Getting Help

- **Stuck?** Check the [Troubleshooting Guide](../reference/troubleshooting.md)
- **Questions?** See the [FAQ](../reference/faq.md)
- **Technical Issues?** Review [Technical Documentation](../technical-documentation/architecture.md)

---

**Previous:** [Configuration Guide](configuration.md)  
**Next:** [User Guide Overview](../user-guide/overview.md)

---

**Ready to dive deeper? Continue to the [User Guide](../user-guide/overview.md) for a complete feature walkthrough!**

