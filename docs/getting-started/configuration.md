# Configuration Guide

This guide explains how to configure SuperSuite with the necessary environment variables and API credentials.

---

## Overview

SuperSuite uses environment variables to store sensitive configuration like database credentials and API keys. These are stored in a `.env` file in the repository root.

⚠️ **Security Note:** Never commit the `.env` file to version control. It should already be in `.gitignore`.

---

## Configuration File Location

The `.env` file should be located at:
```
/Users/harshitchoudhary/Desktop/lyzr-hackathon/.env
```

Or more generally:
```
<repository-root>/.env
```

---

## Creating the .env File

### Step 1: Copy the Template

If a `.env.example` or `.env.template` file exists:
```bash
cp .env.example .env
```

Otherwise, create a new `.env` file:
```bash
touch .env
```

### Step 2: Edit the .env File

Open the `.env` file in your preferred text editor:
```bash
# Using nano
nano .env

# Using vim
vim .env

# Using VS Code
code .env
```

---

## Required Environment Variables

### Snowflake Configuration

Snowflake is used as the primary data warehouse for storing all structured data.

```bash
# Snowflake Account
SNOWFLAKE_ACCOUNT=FHWELTT-XS07400
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_DATABASE=LYZRHACK
SNOWFLAKE_SCHEMA=PUBLIC
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_ROLE=ACCOUNTADMIN
```

**Configuration Details:**
- `SNOWFLAKE_ACCOUNT`: Your Snowflake account identifier (format: `ORGNAME-ACCOUNTNAME`)
- `SNOWFLAKE_USER`: Your Snowflake username
- `SNOWFLAKE_PASSWORD`: Your Snowflake password
- `SNOWFLAKE_DATABASE`: Database name (default: `LYZRHACK`)
- `SNOWFLAKE_SCHEMA`: Schema name (default: `PUBLIC`)
- `SNOWFLAKE_WAREHOUSE`: Compute warehouse name (default: `COMPUTE_WH`)
- `SNOWFLAKE_ROLE`: User role (default: `ACCOUNTADMIN`)

💡 **Tip:** Contact your Snowflake administrator if you don't have these credentials.

### Neo4j Aura Configuration

Neo4j Aura is used as the graph database for storing and querying knowledge graphs.

```bash
# Neo4j Aura
NEO4J_URI=neo4j+s://b70333ab.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
```

**Configuration Details:**
- `NEO4J_URI`: Neo4j Aura connection URI (starts with `neo4j+s://` for secure connection)
- `NEO4J_USER`: Neo4j username (usually `neo4j`)
- `NEO4J_PASSWORD`: Neo4j password

💡 **Tip:** You can find these credentials in your Neo4j Aura console.

### DeepSeek API Configuration

DeepSeek is used for AI-powered schema generation, entity extraction, and chat responses.

```bash
# DeepSeek API
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
```

**Configuration Details:**
- `DEEPSEEK_API_KEY`: Your DeepSeek API key
- `DEEPSEEK_BASE_URL`: DeepSeek API endpoint (default: `https://api.deepseek.com`)
- `DEEPSEEK_MODEL`: Model name (default: `deepseek-chat`)

💡 **Tip:** Obtain your API key from the DeepSeek platform.

### HuggingFace Configuration

HuggingFace is used for generating embeddings for semantic search.

```bash
# HuggingFace API
HUGGINGFACE_API_KEY=your_huggingface_api_key
```

**Configuration Details:**
- `HUGGINGFACE_API_KEY`: Your HuggingFace API token

💡 **Tip:** Generate an API token at [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)

---

## Complete .env File Example

Here's a complete example `.env` file with all required variables:

```bash
# Snowflake Configuration
SNOWFLAKE_ACCOUNT=FHWELTT-XS07400
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_DATABASE=LYZRHACK
SNOWFLAKE_SCHEMA=PUBLIC
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_ROLE=ACCOUNTADMIN

# Neo4j Aura Configuration
NEO4J_URI=neo4j+s://b70333ab.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_neo4j_password

# DeepSeek API Configuration
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat

# HuggingFace Configuration
HUGGINGFACE_API_KEY=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Optional: Application Settings
STREAMLIT_SERVER_PORT=8504
LOG_LEVEL=INFO
```

---

## Verifying Configuration

### Step 1: Check .env File Exists

```bash
ls -la .env
```

**Expected output:** File details showing `.env` exists

### Step 2: Verify Environment Variables Load

Create a test script `test_env.py`:

```python
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check required variables
required_vars = [
    "SNOWFLAKE_ACCOUNT",
    "SNOWFLAKE_USER",
    "SNOWFLAKE_PASSWORD",
    "NEO4J_URI",
    "NEO4J_USER",
    "NEO4J_PASSWORD",
    "DEEPSEEK_API_KEY",
    "HUGGINGFACE_API_KEY"
]

print("Checking environment variables...")
missing = []

for var in required_vars:
    value = os.getenv(var)
    if value:
        # Show first 10 chars for security
        masked = value[:10] + "..." if len(value) > 10 else value
        print(f"✅ {var}: {masked}")
    else:
        print(f"❌ {var}: NOT SET")
        missing.append(var)

if missing:
    print(f"\n⚠️  Missing variables: {', '.join(missing)}")
else:
    print("\n✅ All required variables are set!")
```

Run the test:
```bash
python test_env.py
```

**Expected output:** All variables should show ✅

### Step 3: Test Database Connections

Test Snowflake connection:
```python
import os
from dotenv import load_dotenv
import snowflake.connector

load_dotenv()

try:
    conn = snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE")
    )
    print("✅ Snowflake connection successful!")
    conn.close()
except Exception as e:
    print(f"❌ Snowflake connection failed: {e}")
```

Test Neo4j connection:
```python
import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

try:
    driver = GraphDatabase.driver(
        os.getenv("NEO4J_URI"),
        auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))
    )
    driver.verify_connectivity()
    print("✅ Neo4j connection successful!")
    driver.close()
except Exception as e:
    print(f"❌ Neo4j connection failed: {e}")
```

---

## Security Best Practices

### 1. Never Commit .env File

Ensure `.env` is in `.gitignore`:
```bash
# Check if .env is ignored
git check-ignore .env
```

**Expected output:** `.env` (confirms it's ignored)

### 2. Use Strong Passwords

- Minimum 12 characters
- Mix of uppercase, lowercase, numbers, and symbols
- Avoid common words or patterns

### 3. Rotate API Keys Regularly

- Change API keys every 90 days
- Immediately rotate if compromised
- Use different keys for development and production

### 4. Limit Access

- Only share credentials with authorized team members
- Use role-based access control in Snowflake and Neo4j
- Monitor access logs regularly

### 5. Backup Configuration

- Keep a secure backup of your `.env` file
- Store in encrypted password manager
- Document where credentials can be obtained

---

## Troubleshooting Configuration Issues

### Issue: Environment variables not loading

**Symptom:** Application can't find configuration

**Solution:**
```bash
# Ensure .env is in repository root
ls -la .env

# Check file permissions
chmod 600 .env

# Verify python-dotenv is installed
pip install python-dotenv
```

### Issue: Snowflake connection fails

**Error:** `250001: Could not connect to Snowflake backend`

**Solution:**
1. Verify account identifier format: `ORGNAME-ACCOUNTNAME`
2. Check username and password are correct
3. Ensure warehouse is running
4. Verify network connectivity

### Issue: Neo4j connection fails

**Error:** `ServiceUnavailable: Connection refused`

**Solution:**
1. Verify URI format: `neo4j+s://xxxxx.databases.neo4j.io`
2. Check username (usually `neo4j`)
3. Verify password is correct
4. Ensure Neo4j Aura instance is running

### Issue: DeepSeek API fails

**Error:** `401 Unauthorized`

**Solution:**
1. Verify API key is correct
2. Check API key has not expired
3. Ensure sufficient API credits
4. Verify base URL is correct

### Issue: HuggingFace API fails

**Error:** `Invalid token`

**Solution:**
1. Generate new token at huggingface.co
2. Ensure token has read permissions
3. Verify token is not expired

---

## Next Steps

✅ **Configuration Complete!**

Now proceed to:
1. **[Quick Start Guide](quick-start.md)** - Run SuperSuite for the first time
2. **[User Guide](../user-guide/overview.md)** - Learn how to use all features

---

## Additional Resources

- **Environment Variables Reference:** [Complete list](../reference/environment-variables.md)
- **Troubleshooting:** [Common issues](../reference/troubleshooting.md)
- **Security:** Best practices for credential management

---

**Previous:** [Installation Guide](installation.md)  
**Next:** [Quick Start Guide](quick-start.md)

