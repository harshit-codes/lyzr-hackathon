# Processing Documents

Learn how to process uploaded documents with AI to extract structured knowledge and generate schemas.

---

## Overview

Document processing is the core AI-powered feature of SuperSuite. It analyzes your PDF documents to:
- Extract text content
- Generate entity schemas using DeepSeek AI
- Extract structured entities
- Store data in Snowflake and Neo4j
- Prepare documents for ontology creation

**Processing Time:** 30-60 seconds per document

---

## Prerequisites

Before processing documents:
- ✅ You have uploaded documents (see [Uploading Documents](uploading-documents.md))
- ✅ Documents show status "Uploaded" in the documents list
- ✅ Your project is selected in the sidebar

---

## What Happens During Processing?

### AI-Powered Analysis

SuperSuite performs the following steps automatically:

1. **PDF Parsing** 📄
   - Extracts text from PDF files
   - Preserves document structure
   - Handles multi-page documents

2. **Schema Generation** 🤖
   - Uses DeepSeek AI to analyze content
   - Identifies entity types (Person, Organization, Concept, etc.)
   - Defines attributes for each entity type
   - Creates relationship types

3. **Entity Extraction** 🔍
   - Extracts specific entities from text
   - Populates entity attributes
   - Identifies relationships between entities

4. **Data Storage** 💾
   - Stores schemas in Snowflake
   - Stores entities in Snowflake
   - Syncs to Neo4j graph database
   - Creates vector embeddings

---

## Step-by-Step Guide

### Step 1: Navigate to Documents Tab

1. Ensure your project is selected in the sidebar
2. Click on the **"📄 Documents"** tab
3. Scroll down to view uploaded documents

![Documents Tab](../assets/screenshots/05-upload-interface.png)

---

### Step 2: Verify Uploaded Documents

Check the **"Project Documents"** table:
- Verify your documents are listed
- Check status is "Uploaded" (not "Processed")
- Note the number of documents ready to process

![Uploaded Documents](../assets/screenshots/07-file-uploaded.png)

---

### Step 3: Start Processing

Scroll down to the **"Process Documents"** section.

You'll see:
- Message: "📋 X document(s) ready to process"
- Button: **"🚀 Process All Documents"**

Click the **"🚀 Process All Documents"** button to begin.

![Ready to Process](../assets/screenshots/08-ready-to-process.png)

---

### Step 4: Monitor Processing Progress

Once processing starts, you'll see:

1. **Progress Bar** - Shows overall progress (0% to 100%)
2. **Status Text** - Shows current document being processed
3. **Spinner** - Indicates AI is working

**Example Status Messages:**
```
Processing resume-harshit.pdf...
Processing company-report.pdf...
Processing complete!
```

![Processing in Progress](../assets/screenshots/09-processing-in-progress.png)

**Important:**
- ⏳ Don't close the browser tab
- ⏳ Don't navigate away from the page
- ⏳ Wait for the success message

---

### Step 5: Verify Processing Complete

After processing completes, you'll see:
- ✅ Success message: "All documents processed successfully!"
- 📊 Document status changes to "Processed"
- 🔄 Page automatically refreshes

![Processing Complete](../assets/screenshots/10-processing-complete.png)

---

### Step 6: Review Processed Documents

Check the **"Project Documents"** table again:

| Filename | Size | Status | Uploaded |
|----------|------|--------|----------|
| resume-harshit.pdf | 111.2 KB | **Processed** | 2025-10-16 10:30 |

**Status Changed:**
- Before: "Uploaded"
- After: "Processed" ✅

---

## Processing Results

### What Gets Created

After processing, SuperSuite creates:

1. **Schemas** 🏗️
   - Entity type definitions
   - Attribute specifications
   - Relationship types
   - Stored in Snowflake

2. **Entities** 👤
   - Extracted instances
   - Populated attributes
   - Unique identifiers
   - Stored in Snowflake

3. **Relationships** 🔗
   - Connections between entities
   - Relationship types
   - Properties
   - Stored in Neo4j

4. **Embeddings** 🧠
   - Vector representations
   - Semantic search capability
   - Stored in Snowflake

---

### Example Processing Output

**For a Resume Document:**

**Schemas Created:**
- Person (attributes: name, role, email, phone)
- Organization (attributes: name, industry, location)
- Skill (attributes: name, proficiency, category)
- Education (attributes: degree, institution, year)

**Entities Extracted:**
- Person: "Harshit Choudhary"
- Organizations: "TechCorp", "DataSystems Inc"
- Skills: "Python", "Machine Learning", "SQL"
- Education: "B.Tech Computer Science"

**Relationships:**
- Harshit → WORKS_FOR → TechCorp
- Harshit → HAS_SKILL → Python
- Harshit → STUDIED_AT → University

---

## Processing Time

### Expected Duration

| Document Size | Processing Time |
|---------------|-----------------|
| Small (< 1 MB) | 30-45 seconds |
| Medium (1-5 MB) | 45-90 seconds |
| Large (5-10 MB) | 90-180 seconds |

**Factors Affecting Speed:**
- Document length (number of pages)
- Content complexity
- Number of entities
- API response time (DeepSeek)
- Network latency

---

## Best Practices

### Before Processing
1. **Verify Upload** - Ensure all documents uploaded successfully
2. **Check Format** - Confirm files are text-based PDFs
3. **Review Content** - Ensure documents contain relevant information
4. **Stable Connection** - Use reliable internet connection

### During Processing
1. **Don't Navigate Away** - Stay on the page
2. **Don't Refresh** - Let processing complete
3. **Monitor Progress** - Watch status messages
4. **Be Patient** - AI analysis takes time

### After Processing
1. **Verify Status** - Check all documents show "Processed"
2. **Review Results** - Check ontology and knowledge base
3. **Validate Data** - Ensure entities were extracted correctly
4. **Report Issues** - Note any errors or unexpected results

---

## Troubleshooting

### Processing Fails
**Problem:** Error message appears during processing

**Solutions:**
1. Check document format (must be text-based PDF)
2. Verify file is not corrupted
3. Check API credentials (DeepSeek, Snowflake)
4. Try processing one document at a time
5. Check error message for specific details

---

### Processing Takes Too Long
**Problem:** Processing exceeds expected time

**Solutions:**
1. Check document size (large files take longer)
2. Verify internet connection is stable
3. Check API rate limits (DeepSeek)
4. Wait patiently - complex documents need more time
5. If stuck >5 minutes, refresh and try again

---

### No Entities Extracted
**Problem:** Processing completes but no entities found

**Solutions:**
1. Check document content (must contain structured information)
2. Verify PDF is text-based (not scanned image)
3. Review document in Ontology tab
4. Check Snowflake for data
5. Try re-processing the document

---

### Status Doesn't Update
**Problem:** Document still shows "Uploaded" after processing

**Solutions:**
1. Refresh the page (Ctrl+R or Cmd+R)
2. Check for error messages
3. Verify processing completed successfully
4. Check browser console for errors
5. Try processing again

---

## Technical Details

### AI Models Used

**DeepSeek AI:**
- Schema generation
- Entity extraction
- Relationship identification
- Natural language understanding

**HuggingFace:**
- Text embeddings
- Semantic similarity
- Vector representations

---

### Data Storage

**Snowflake:**
- Schema definitions
- Entity instances
- Document metadata
- Vector embeddings

**Neo4j Aura:**
- Graph structure
- Entity relationships
- Cypher queries
- Graph traversal

---

## Next Steps

After processing documents:

1. **Generate Ontology** → [Viewing Ontology](viewing-ontology.md)
   - Review entity types
   - Examine relationships
   - Understand document structure

2. **Extract Knowledge** → [Exploring Knowledge](exploring-knowledge.md)
   - Browse extracted entities
   - View entity details
   - Explore relationships

3. **Query with Chat** → [Querying with Chat](querying-chat.md)
   - Ask questions about your documents
   - Get AI-powered insights
   - Explore knowledge interactively

---

## Quick Reference

### Processing Workflow
```
1. Upload Documents → 2. Verify Upload → 3. Click Process → 4. Monitor Progress → 5. Verify Complete
```

### Processing Checklist
- [ ] Documents uploaded successfully
- [ ] Status shows "Uploaded"
- [ ] Clicked "Process All Documents"
- [ ] Waited for completion
- [ ] Status changed to "Processed"
- [ ] Success message appeared

### Common Issues
| Issue | Solution |
|-------|----------|
| Processing fails | Check file format and API credentials |
| Takes too long | Wait patiently, check document size |
| No entities | Verify PDF is text-based |
| Status not updated | Refresh page |

---

## Related Topics

- [Uploading Documents](uploading-documents.md) - Upload documents before processing
- [Viewing Ontology](viewing-ontology.md) - Review processing results
- [Configuration](../getting-started/configuration.md) - Configure API credentials
- [Troubleshooting](../reference/troubleshooting.md) - Resolve common issues

---

## Need Help?

- 📖 [FAQ](../reference/faq.md) - Frequently asked questions
- 🔧 [Troubleshooting](../reference/troubleshooting.md) - Common issues and solutions
- 💬 [Support](../README.md#support) - Get help from the team

---

**Previous:** [Uploading Documents](uploading-documents.md) | **Next:** [Viewing Ontology](viewing-ontology.md)

