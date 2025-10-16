# Creating Projects

Projects are the foundation of SuperSuite's organization system. Each project contains documents, schemas, entities, and relationships related to a specific domain or use case.

---

## What is a Project?

A **project** in SuperSuite is a container that organizes:
- 📄 **Documents:** PDF files you upload
- 🎨 **Schemas:** Entity types and relationship definitions
- 📊 **Entities:** Extracted knowledge (people, organizations, concepts, etc.)
- 🔗 **Relationships:** Connections between entities
- 💬 **Chat History:** Your questions and answers

Think of a project as a dedicated knowledge base for a specific topic or collection of documents.

---

## When to Create a New Project

Create a new project when you want to:
- ✅ Analyze a new collection of documents
- ✅ Build a knowledge base for a specific domain
- ✅ Keep different document types separated
- ✅ Organize work by client, department, or topic

**Examples:**
- "Research Papers - Machine Learning"
- "Company Policies 2025"
- "Customer Support Tickets - Q1"
- "Legal Contracts - Vendor Agreements"

---

## Creating a Project

### Step 1: Access Project Creation

📸 **Screenshot Placeholder:** *Sidebar with "Create New Project" section*

1. Open SuperSuite in your browser (`http://localhost:8504`)
2. Look at the **sidebar** on the left
3. Find the **"Create New Project"** section

### Step 2: Enter Project Details

📸 **Screenshot Placeholder:** *Project creation form with fields*

Fill in the project information:

#### Project Name (Required)
- **Purpose:** Unique identifier for your project
- **Format:** Short, descriptive name
- **Examples:**
  - `Resume Analysis - Harshit`
  - `AI Research Papers`
  - `Company Policies`
  - `Legal Contracts 2025`

**Best Practices:**
- Use clear, descriptive names
- Include dates or versions if relevant
- Avoid special characters
- Keep it concise (< 50 characters)

#### Project Description (Required)
- **Purpose:** Detailed explanation of the project
- **Format:** Free text, 1-3 sentences
- **Examples:**
  - `End-to-end test with resume document`
  - `Collection of machine learning research papers from 2020-2025`
  - `All company policy documents for employee reference`
  - `Vendor contracts requiring annual review`

**Best Practices:**
- Explain the project's purpose
- Mention the type of documents
- Note any special requirements
- Include relevant context

### Step 3: Create the Project

📸 **Screenshot Placeholder:** *Create button and success message*

1. **Review** your project name and description
2. **Click** the "Create" or "Create Project" button
3. **Wait** for confirmation (usually instant)

**Expected Result:**
- ✅ Success message appears
- ✅ Project appears in the project dropdown
- ✅ Project is automatically selected
- ✅ Ready to upload documents

---

## Managing Projects

### Selecting a Project

📸 **Screenshot Placeholder:** *Project dropdown menu*

To work with an existing project:

1. Find the **"Select Project"** dropdown in the sidebar
2. Click the dropdown to see all your projects
3. Select the project you want to work with

**What happens:**
- The selected project becomes active
- All views show data for this project only
- Document uploads go to this project
- Chat queries search this project's knowledge

### Viewing Project Information

📸 **Screenshot Placeholder:** *Project details display*

Once a project is selected, you can see:
- **Project Name:** Displayed in the sidebar
- **Document Count:** Number of uploaded documents
- **Entity Count:** Number of extracted entities
- **Last Updated:** When the project was last modified

### Switching Between Projects

To switch to a different project:
1. Click the project dropdown
2. Select a different project
3. The interface updates to show the new project's data

💡 **Tip:** Each project maintains its own independent knowledge base.

---

## Project Best Practices

### Naming Conventions

**Good Project Names:**
- ✅ `Research Papers - NLP 2024`
- ✅ `Customer Support - Technical Issues`
- ✅ `Legal - Employment Contracts`
- ✅ `Marketing - Campaign Analysis`

**Poor Project Names:**
- ❌ `Project1`
- ❌ `Test`
- ❌ `Untitled`
- ❌ `asdfgh`

### Organization Strategies

#### Strategy 1: By Document Type
```
- Research Papers
- Technical Documentation
- Legal Contracts
- Company Policies
```

#### Strategy 2: By Time Period
```
- Q1 2025 Reports
- Q2 2025 Reports
- Annual Review 2024
```

#### Strategy 3: By Client/Department
```
- Client A - Contracts
- Client B - Contracts
- HR Department Docs
- Engineering Docs
```

#### Strategy 4: By Topic
```
- Machine Learning Research
- Natural Language Processing
- Computer Vision
- Robotics
```

### Project Scope

**Optimal Project Size:**
- 📄 **Documents:** 1-100 documents per project
- 📊 **Entities:** Up to 10,000 entities
- 🔗 **Relationships:** Up to 50,000 relationships

**When to Split Projects:**
- Project becomes too large (> 100 documents)
- Documents cover different domains
- Need separate access control
- Performance degrades

---

## Common Use Cases

### Use Case 1: Research Paper Collection

**Project Name:** `AI Research Papers - 2024`

**Description:** `Collection of artificial intelligence research papers published in 2024 for literature review and analysis.`

**Documents:** 20-50 research papers

**Expected Entities:** Authors, Papers, Concepts, Methods, Datasets

### Use Case 2: Company Knowledge Base

**Project Name:** `Company Policies and Procedures`

**Description:** `All company policy documents, employee handbooks, and standard operating procedures for easy reference.`

**Documents:** 10-30 policy documents

**Expected Entities:** Policies, Departments, Requirements, Procedures, Roles

### Use Case 3: Resume Screening

**Project Name:** `Job Candidates - Data Scientist Role`

**Description:** `Resumes of candidates applying for the Data Scientist position, for skills analysis and comparison.`

**Documents:** 50-100 resumes

**Expected Entities:** Candidates, Skills, Experience, Education, Certifications

### Use Case 4: Legal Document Analysis

**Project Name:** `Vendor Contracts - 2025 Renewals`

**Description:** `Vendor contracts up for renewal in 2025, for terms review and negotiation preparation.`

**Documents:** 10-20 contracts

**Expected Entities:** Vendors, Terms, Obligations, Dates, Payment Terms

---

## Troubleshooting

### Issue: Project creation fails

**Symptom:** Error message when clicking "Create"

**Possible Causes:**
- Empty project name or description
- Duplicate project name
- Database connection issue

**Solutions:**
1. Ensure both name and description are filled
2. Use a unique project name
3. Check database connection status
4. Refresh the page and try again

### Issue: Project doesn't appear in dropdown

**Symptom:** Created project not visible in selection dropdown

**Solutions:**
1. Refresh the page
2. Check for error messages
3. Verify database connection
4. Try creating the project again

### Issue: Can't select a project

**Symptom:** Dropdown is disabled or empty

**Solutions:**
1. Create a project first
2. Refresh the page
3. Check browser console for errors
4. Verify application is running

---

## Next Steps

✅ **Project Created!**

Now that you have a project, you can:

1. **[Upload Documents](uploading-documents.md)** - Add PDF files to your project
2. **[Process Documents](processing-documents.md)** - Extract knowledge with AI
3. **[View Ontology](viewing-ontology.md)** - Explore entity types
4. **[Explore Knowledge](exploring-knowledge.md)** - Browse extracted entities
5. **[Query with Chat](querying-chat.md)** - Ask questions

---

## Additional Resources

- **[User Guide Overview](overview.md)** - Complete workflow guide
- **[Troubleshooting](../reference/troubleshooting.md)** - Common issues
- **[FAQ](../reference/faq.md)** - Frequently asked questions

---

**Previous:** [User Guide Overview](overview.md)  
**Next:** [Uploading Documents](uploading-documents.md)

---

**Ready to add documents? Continue to [Uploading Documents](uploading-documents.md) →**

