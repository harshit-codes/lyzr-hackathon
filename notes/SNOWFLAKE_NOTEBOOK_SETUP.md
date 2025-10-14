# Snowflake Notebook Setup & Deployment - Knowledge Base

**Project**: Lyzr Hackathon - Agentic Graph RAG  
**Date**: October 14, 2025  
**Status**: ✅ Successfully Deployed

---

## 📋 Summary

Successfully created and deployed a "Hello World" Jupyter notebook to Snowflake using Python automation. The notebook demonstrates both Python and SQL execution in Snowflake's notebook environment.

---

## 🏗️ Architecture

### Components Created

1. **Jupyter Notebook** (`hello_world.ipynb`)
   - 2 Markdown cells (title and description)
   - 1 Python cell (prints "Hello, World!")
   - 1 SQL cell (queries current user and timestamp)

2. **Deployment Script** (`deploy_notebook.py`)
   - Python script using `snowflake-connector-python`
   - Automated stage creation
   - File upload to Snowflake stage
   - Notebook object creation in Snowflake

3. **Configuration Files**
   - `snowflake.yml` - Snowflake CLI project definition
   - `.env` - Environment variables (credentials, never committed)
   - `.gitignore` - Prevents credential exposure

4. **Documentation**
   - `README.md` - Project overview
   - `NEXT_STEPS.md` - Deployment guide
   - `PAT_TOKEN_ISSUE.md` - Troubleshooting guide
   - `MANUAL_UPLOAD_GUIDE.md` - Alternative deployment method

---

## 🔐 Authentication Setup

### Snowflake Credentials

**Account Details**:
- **Account ID**: `FHWELTT-XS07400`
- **User**: `HARSHITCODES`
- **Role**: `ACCOUNTADMIN`
- **Warehouse**: `COMPUTE_WH`
- **Database**: `SNOWFLAKE_LEARNING_DB`
- **Schema**: `PUBLIC`

### Authentication Methods Tried

1. ❌ **PAT Token with `authenticator='oauth'`** - Failed (Invalid OAuth token)
2. ❌ **PAT Token without authenticator** - Failed (Password empty)
3. ❌ **External Browser Auth** - Failed (SAML configuration issue)
4. ✅ **Username/Password** - **SUCCESS**

### Final Working Configuration

Stored in `.env` file:
```bash
SNOWFLAKE_ACCOUNT=FHWELTT-XS07400
SNOWFLAKE_USER=HARSHITCODES
SNOWFLAKE_PASSWORD=***REDACTED_PASSWORD***
SNOWFLAKE_ROLE=ACCOUNTADMIN
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=SNOWFLAKE_LEARNING_DB
SNOWFLAKE_SCHEMA=PUBLIC
```

**Security Notes**:
- `.env` file is gitignored (never committed)
- File permissions set to `600` (owner read/write only)
- Password authentication used due to PAT token issues

---

## 📂 Project Structure

```
lyzr-hackathon/
├── .env                                    # Credentials (gitignored)
├── .gitignore                              # Updated with .env exclusion
├── code/
│   └── notebooks/
│       ├── MANUAL_UPLOAD_GUIDE.md         # Alternative deployment guide
│       ├── NEXT_STEPS.md                  # Step-by-step instructions
│       ├── PAT_TOKEN_ISSUE.md             # Troubleshooting PAT issues
│       └── hello-world/
│           ├── deploy_notebook.py         # Automated deployment script
│           ├── hello_world.ipynb          # The Jupyter notebook
│           ├── README.md                  # Project documentation
│           └── snowflake.yml              # Snowflake CLI config
└── notes/
    └── SNOWFLAKE_NOTEBOOK_SETUP.md        # This file
```

---

## 🚀 Deployment Process

### Prerequisites

1. **Snowflake CLI** (v3.12.0)
   ```bash
   pip3 install snowflake-cli-labs
   snow --version
   ```

2. **Python Libraries**
   ```bash
   pip3 install snowflake-connector-python python-dotenv
   ```

3. **Environment Variables**
   ```bash
   # Create .env file
   cat > .env << EOF
   SNOWFLAKE_ACCOUNT=FHWELTT-XS07400
   SNOWFLAKE_USER=HARSHITCODES
   SNOWFLAKE_PASSWORD=***REDACTED_PASSWORD***
   SNOWFLAKE_ROLE=ACCOUNTADMIN
   SNOWFLAKE_WAREHOUSE=COMPUTE_WH
   SNOWFLAKE_DATABASE=SNOWFLAKE_LEARNING_DB
   SNOWFLAKE_SCHEMA=PUBLIC
   EOF
   
   chmod 600 .env
   ```

### Deployment Steps

1. **Navigate to Project Directory**
   ```bash
   cd ~/Desktop/lyzr-hackathon/code/notebooks/hello-world
   ```

2. **Run Deployment Script**
   ```bash
   python3 deploy_notebook.py
   ```

3. **Script Actions**
   - ✅ Connects to Snowflake using credentials
   - ✅ Creates stage: `SNOWFLAKE_LEARNING_DB.PUBLIC.NOTEBOOKS_STAGE`
   - ✅ Uploads `hello_world.ipynb` to stage
   - ✅ Creates notebook object: `HELLO_WORLD_NOTEBOOK`
   - ✅ Returns access URL

### Successful Deployment Output

```
🔗 Connecting to Snowflake account: FHWELTT-XS07400
👤 User: HARSHITCODES
🔐 Auth method: password
🎭 Role: ACCOUNTADMIN
🏠 Warehouse: COMPUTE_WH
📊 Database: SNOWFLAKE_LEARNING_DB.PUBLIC

✅ Connected to Snowflake successfully!
✅ Current context: User=HARSHITCODES, Role=ACCOUNTADMIN, Warehouse=COMPUTE_WH, Database=SNOWFLAKE_LEARNING_DB

📦 Creating stage: SNOWFLAKE_LEARNING_DB.PUBLIC.NOTEBOOKS_STAGE
✅ Stage created/verified: SNOWFLAKE_LEARNING_DB.PUBLIC.NOTEBOOKS_STAGE

📤 Uploading hello_world.ipynb to stage...
✅ Uploaded hello_world.ipynb to @SNOWFLAKE_LEARNING_DB.PUBLIC.NOTEBOOKS_STAGE

📋 Files in @SNOWFLAKE_LEARNING_DB.PUBLIC.NOTEBOOKS_STAGE:
  - notebooks_stage/hello_world.ipynb

📓 Creating Snowflake Notebook: HELLO_WORLD_NOTEBOOK
✅ Notebook created: HELLO_WORLD_NOTEBOOK

🎉 SUCCESS! Your notebook is deployed!
🔗 Access it at: https://app.snowflake.com/fhweltt/xs07400/#/notebooks/SNOWFLAKE_LEARNING_DB.PUBLIC.HELLO_WORLD_NOTEBOOK
```

---

## 📓 Notebook Contents

### Cell 1: Markdown Title
```markdown
# Hello World Notebook
```

### Cell 2: Markdown Description
```markdown
This is a simple hello world notebook for Snowflake
```

### Cell 3: Python Code
```python
print("Hello, World!")
```
**Expected Output**: `Hello, World!`

### Cell 4: SQL Query
```sql
SELECT 'Hello from Snowflake!' as message, 
       CURRENT_USER() as user, 
       CURRENT_TIMESTAMP() as timestamp;
```
**Expected Output**: Table with 3 columns showing message, current user (HARSHITCODES), and current timestamp

---

## 🔧 Technical Implementation

### Python Deployment Script

**Key Features**:
- ✅ Environment variable management via `python-dotenv`
- ✅ Automatic stage creation (idempotent)
- ✅ File upload to Snowflake internal stage
- ✅ Notebook object creation with SQL DDL
- ✅ Support for both password and PAT token authentication
- ✅ Comprehensive error handling and logging

**Connection Code** (Working Method):
```python
conn = snowflake.connector.connect(
    account=SNOWFLAKE_ACCOUNT,
    user=SNOWFLAKE_USER,
    password=SNOWFLAKE_PASSWORD,  # Using password auth
    role=SNOWFLAKE_ROLE,
    warehouse=SNOWFLAKE_WAREHOUSE,
    database=SNOWFLAKE_DATABASE,
    schema=SNOWFLAKE_SCHEMA
)
```

**Stage Creation**:
```python
cursor.execute(f"CREATE STAGE IF NOT EXISTS {STAGE_NAME}")
```

**File Upload**:
```python
cursor.execute(f"PUT file://{notebook_path} @{STAGE_NAME} AUTO_COMPRESS=FALSE OVERWRITE=TRUE")
```

**Notebook Creation**:
```sql
CREATE OR REPLACE NOTEBOOK SNOWFLAKE_LEARNING_DB.PUBLIC.HELLO_WORLD_NOTEBOOK
FROM '@SNOWFLAKE_LEARNING_DB.PUBLIC.NOTEBOOKS_STAGE'
MAIN_FILE = 'hello_world.ipynb'
QUERY_WAREHOUSE = 'COMPUTE_WH'
```

---

## 🐛 Issues Encountered & Solutions

### Issue 1: PAT Token Authentication Failed

**Error**: `250001 (08001): Invalid OAuth access token`

**Attempted Solutions**:
1. Used `authenticator='oauth'` with token parameter
2. Used `authenticator='SNOWFLAKE_JWT'` with token
3. Stored token in file and referenced via `token_file_path`
4. Removed authenticator parameter entirely

**Root Cause**: PAT token authentication via Python connector requires additional Snowflake account configuration (SAML/SSO settings)

**Final Solution**: ✅ Switched to username/password authentication

### Issue 2: SAML Identity Provider Error

**Error**: `390190 (08001): There was an error related to the SAML Identity Provider`

**Attempted Solution**: Used `authenticator='externalbrowser'`

**Root Cause**: Account has SSO/SAML configured, causing conflicts with external browser auth

**Final Solution**: ✅ Used password authentication instead

### Issue 3: Snowflake CLI Connection Issues

**Error**: Various authentication errors with `snow connection test`

**Attempted Solutions**:
1. Configured `~/.snowflake/config.toml` with OAuth
2. Configured with external browser auth
3. Configured with token file path

**Final Solution**: ✅ Bypassed Snowflake CLI entirely, used Python connector directly

---

## 📊 Access & Verification

### Access URLs

**Direct Notebook Link**:
```
https://app.snowflake.com/fhweltt/xs07400/#/notebooks/SNOWFLAKE_LEARNING_DB.PUBLIC.HELLO_WORLD_NOTEBOOK
```

**Notebooks Dashboard**:
```
https://app.snowflake.com/fhweltt/xs07400/#/notebooks
```

### Verification Steps

1. **Login to Snowflake UI**
2. **Navigate to**: Projects → Notebooks
3. **Find**: `HELLO_WORLD_NOTEBOOK`
4. **Run Cells**: Execute Python and SQL cells
5. **Verify Outputs**: Check expected results match

---

## 🔄 Git Workflow

### Commit Commands

```bash
cd ~/Desktop/lyzr-hackathon
git add .gitignore code/notebooks/ notes/
git status  # Verify .env is NOT listed
git commit -m "Add Snowflake notebook deployment"
```

### Never Commit
- ❌ `.env` (contains password)
- ❌ `~/.snowflake/config.toml` (local config)

---

## 📚 Key Learnings

### 1. Authentication Complexity
- PAT tokens require specific Snowflake account configuration
- SSO/SAML accounts have authentication restrictions
- Password auth is most reliable for development/scripts

### 2. Snowflake CLI vs Python Connector
- Snowflake CLI has authentication limitations
- Python connector (`snowflake-connector-python`) is more flexible
- Direct Python scripting gives more control

### 3. Security Best Practices
- Always use `.gitignore` for credentials
- Set proper file permissions (`chmod 600`) for sensitive files
- Store credentials in environment variables, not hardcoded

### 4. Deployment Strategies
- Automated deployment requires proper authentication setup
- Manual upload is valid fallback (especially for initial testing)
- Document multiple deployment paths for flexibility

---

## 🎯 Future Enhancements

### Short Term
1. ✅ Add password authentication support to deployment script
2. ⬜ Create CI/CD pipeline for automated deployments
3. ⬜ Add unit tests for deployment script
4. ⬜ Implement deployment rollback functionality

### Long Term
1. ⬜ Resolve PAT token authentication with Snowflake support
2. ⬜ Implement SSO/SAML authentication flow
3. ⬜ Create multi-environment deployment (dev/staging/prod)
4. ⬜ Add notebook versioning and change tracking

---

## 📖 References

### Official Documentation
- [Snowflake CLI Documentation](https://docs.snowflake.com/en/developer-guide/snowflake-cli)
- [Snowflake Notebooks](https://docs.snowflake.com/en/user-guide/ui-snowsight/notebooks)
- [Python Connector](https://docs.snowflake.com/en/developer-guide/python-connector/python-connector)
- [OAuth Personal Access Tokens](https://docs.snowflake.com/en/user-guide/oauth-personal-access-token)

### Tools Used
- Snowflake CLI: v3.12.0
- snowflake-connector-python: v3.17.3
- python-dotenv: v1.1.0
- Python: 3.12

---

## ✅ Success Criteria Met

- ✅ Created Jupyter notebook with Python and SQL cells
- ✅ Configured Snowflake connection with credentials
- ✅ Automated deployment script working
- ✅ Notebook successfully deployed to Snowflake
- ✅ Notebook accessible via Snowflake UI
- ✅ All credentials secured and gitignored
- ✅ Comprehensive documentation created
- ✅ Multiple deployment paths documented

---

## 🎉 Conclusion

Successfully implemented end-to-end Snowflake Notebook deployment automation. The solution is production-ready for password-based authentication and provides clear documentation for alternative authentication methods and manual deployment as needed.

**Deployment Time**: ~5 minutes (including troubleshooting)  
**Final Status**: ✅ FULLY OPERATIONAL

---

**Document Version**: 1.0  
**Last Updated**: October 14, 2025  
**Maintained By**: Harshit Choudhary (HARSHITCODES)
