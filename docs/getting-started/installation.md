# Installation Guide

This guide will walk you through installing SuperSuite on your system.

---

## System Requirements

### Minimum Requirements
- **Operating System:** macOS, Linux, or Windows 10/11
- **Python:** 3.10 or higher (3.12 recommended)
- **RAM:** 4 GB minimum, 8 GB recommended
- **Disk Space:** 2 GB for application and dependencies
- **Internet Connection:** Required for API access and database connections

### Recommended Requirements
- **Python:** 3.12
- **RAM:** 16 GB
- **Disk Space:** 10 GB (for documents and local caching)
- **Network:** Stable broadband connection

---

## Prerequisites

Before installing SuperSuite, ensure you have the following:

### 1. Python Installation

Check your Python version:
```bash
python --version
# or
python3 --version
```

**Expected output:** `Python 3.10.x` or higher

If you need to install Python:
- **macOS:** Use Homebrew: `brew install python@3.12`
- **Linux:** Use your package manager: `sudo apt install python3.12`
- **Windows:** Download from [python.org](https://www.python.org/downloads/)

### 2. pip (Python Package Manager)

Check if pip is installed:
```bash
pip --version
# or
pip3 --version
```

**Expected output:** `pip 23.x.x` or higher

### 3. Git (Optional, for cloning repository)

Check if Git is installed:
```bash
git --version
```

If not installed:
- **macOS:** `brew install git`
- **Linux:** `sudo apt install git`
- **Windows:** Download from [git-scm.com](https://git-scm.com/)

---

## Installation Steps

### Step 1: Clone or Download the Repository

**Option A: Clone with Git (Recommended)**
```bash
git clone <repository-url>
cd lyzr-hackathon
```

**Option B: Download ZIP**
1. Download the repository as a ZIP file
2. Extract to your desired location
3. Navigate to the extracted directory

### Step 2: Create a Virtual Environment (Recommended)

Creating a virtual environment isolates SuperSuite's dependencies from your system Python.

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

**Expected output:** Your terminal prompt should now show `(venv)` prefix.

💡 **Tip:** Always activate the virtual environment before running SuperSuite.

### Step 3: Install Dependencies

Install all required Python packages:

```bash
pip install -r requirements.txt
```

This will install:
- `streamlit` - Web application framework
- `snowflake-connector-python` - Snowflake database connector
- `snowflake-sqlalchemy` - SQLAlchemy support for Snowflake
- `sqlmodel` - ORM for database operations
- `neo4j` - Neo4j graph database driver
- `openai` - OpenAI API client (for DeepSeek compatibility)
- `langchain` - LLM framework
- `pypdf2` - PDF processing
- `pdfplumber` - Advanced PDF text extraction
- `python-dotenv` - Environment variable management
- And many more...

**Expected output:** Successful installation messages for all packages.

⚠️ **Note:** Installation may take 5-10 minutes depending on your internet connection.

### Step 4: Verify Installation

Check that key packages are installed:

```bash
pip list | grep streamlit
pip list | grep snowflake
pip list | grep neo4j
```

**Expected output:** Version numbers for each package.

---

## Database and API Setup

SuperSuite requires access to external services. You'll need accounts and credentials for:

### 1. Snowflake Account
- **Purpose:** Data warehouse for storing projects, documents, entities, and relationships
- **Setup:** You should have received Snowflake credentials
- **Required:** Account URL, username, password, database name, warehouse

### 2. Neo4j Aura Account
- **Purpose:** Graph database for knowledge graph storage and queries
- **Setup:** You should have received Neo4j Aura credentials
- **Required:** URI, username, password

### 3. DeepSeek API Key
- **Purpose:** AI/LLM for schema generation, entity extraction, and chat
- **Setup:** Obtain API key from DeepSeek
- **Required:** API key, base URL

### 4. HuggingFace API Key
- **Purpose:** Embeddings for semantic search
- **Setup:** Create account at huggingface.co and generate API key
- **Required:** API key

💡 **Tip:** Keep all credentials secure and never commit them to version control.

---

## Configuration

After installation, you need to configure environment variables. See the [Configuration Guide](configuration.md) for detailed instructions.

---

## Verification

To verify your installation is complete:

### 1. Check Python Environment

```bash
# Ensure virtual environment is activated
which python
# Should show path to venv/bin/python
```

### 2. Check Installed Packages

```bash
pip list | wc -l
# Should show 50+ packages installed
```

### 3. Test Import

```bash
python -c "import streamlit; import snowflake.connector; import neo4j; print('✅ All imports successful')"
```

**Expected output:** `✅ All imports successful`

---

## Troubleshooting Installation Issues

### Issue: Python version too old

**Error:** `Python 3.9 or lower detected`

**Solution:**
```bash
# Install Python 3.12
brew install python@3.12  # macOS
# or
sudo apt install python3.12  # Linux

# Create venv with specific Python version
python3.12 -m venv venv
```

### Issue: pip install fails

**Error:** `ERROR: Could not find a version that satisfies the requirement...`

**Solution:**
```bash
# Upgrade pip
pip install --upgrade pip

# Try installing again
pip install -r requirements.txt
```

### Issue: Permission denied

**Error:** `Permission denied` when installing packages

**Solution:**
```bash
# Use virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# OR install with --user flag (not recommended)
pip install --user -r requirements.txt
```

### Issue: Snowflake connector fails to install

**Error:** `Failed building wheel for snowflake-connector-python`

**Solution:**
```bash
# Install build dependencies
# macOS:
brew install openssl

# Linux:
sudo apt-get install build-essential libssl-dev libffi-dev python3-dev

# Try again
pip install snowflake-connector-python
```

### Issue: Neo4j driver fails to install

**Error:** `Failed to install neo4j`

**Solution:**
```bash
# Ensure you have the correct package name
pip install neo4j

# If still fails, try upgrading pip
pip install --upgrade pip setuptools wheel
pip install neo4j
```

---

## Next Steps

✅ **Installation Complete!**

Now proceed to:
1. **[Configuration Guide](configuration.md)** - Set up environment variables and API keys
2. **[Quick Start](quick-start.md)** - Run SuperSuite for the first time

---

## Additional Resources

- **Python Virtual Environments:** [Python venv documentation](https://docs.python.org/3/library/venv.html)
- **pip Documentation:** [pip.pypa.io](https://pip.pypa.io/)
- **Troubleshooting:** [Common Issues](../reference/troubleshooting.md)

---

**Previous:** [Documentation Home](../README.md)  
**Next:** [Configuration Guide](configuration.md)

