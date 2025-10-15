# SuperScan Snowflake Setup Instructions

## Prerequisites

- Snowflake account with access credentials
- Python 3.8+ installed
- Required Python packages (see requirements)

## Step 1: Generate Snowflake Personal Access Token

1. **Log in to Snowflake UI**
   - Open your browser and go to: `https://<your_account>.snowflakecomputing.com`
   - Log in with your credentials

2. **Navigate to Personal Access Tokens**
   - Click on your profile (top right)
   - Select **"Personal Access Tokens"**

3. **Generate New Token**
   - Click **"Generate New Token"**
   - Name: `superscan-dev-token`
   - Expiration: 90 days (or your preference)
   - Click **"Generate"**

4. **Copy Token**
   - ⚠️ **IMPORTANT**: Copy the token immediately (shown only once!)
   - Save it temporarily in a secure location

## Step 2: Create .env File

1. **Navigate to code directory**
   ```bash
   cd /Users/harshitchoudhary/Desktop/lyzr-hackathon/code
   ```

2. **Create .env file from template**
   ```bash
   cp .env.example .env
   ```

3. **Edit .env file** (use nano, vim, or VS Code)
   ```bash
   nano .env
   ```

4. **Fill in your Snowflake credentials:**
   ```bash
   # Snowflake Configuration
   SNOWFLAKE_ACCOUNT=<your_account_identifier>    # e.g., abc12345.us-west-2.aws
   SNOWFLAKE_USER=<your_username>                  # Your Snowflake username
   SNOWFLAKE_AUTHENTICATOR=PROGRAMMATIC_ACCESS_TOKEN
   SNOWFLAKE_PAT=<paste_your_token_here>          # Token from Step 1
   
   # Database settings
   SNOWFLAKE_DATABASE=superscan
   SNOWFLAKE_SCHEMA=public
   SNOWFLAKE_WAREHOUSE=COMPUTE_WH
   SNOWFLAKE_ROLE=ACCOUNTADMIN
   
   # DeepSeek API Key (optional for LLM-powered ontology generation)
   DEEPSEEK_API_KEY=<your_deepseek_key>
   
   # OpenAI API Key (optional for embeddings)
   OPENAI_API_KEY=<your_openai_key>
   ```

5. **Save and exit** (Ctrl+O, Enter, Ctrl+X if using nano)

6. **Verify .env file exists**
   ```bash
   ls -la .env
   ```

### Finding Your Snowflake Account Identifier

- **Format**: `<account_locator>.<region>.<cloud>`
- **Example**: `abc12345.us-west-2.aws`

**Where to find it:**
1. In Snowflake UI, look at your URL
2. It's the part before `.snowflakecomputing.com`
3. Example: `https://abc12345.us-west-2.aws.snowflakecomputing.com` → Account: `abc12345.us-west-2.aws`

## Step 3: Run Setup Script

This script will:
- ✅ Verify Snowflake connection
- ✅ Create database and schema
- ✅ Initialize all tables
- ✅ Run end-to-end SuperScan test
- ✅ Display created data

**Run the setup:**
```bash
python scripts/setup_snowflake.py
```

**Expected Output:**
```
================================================================================
 SuperScan Snowflake Setup
================================================================================

This script will:
  1. Check environment variables
  2. Test Snowflake connection
  3. Create database and schema
  4. Initialize tables
  5. Verify tables
  6. Run SuperScan end-to-end test
  7. Query and display data

================================================================================
 Step 1: Checking Environment Variables
================================================================================

✓ SNOWFLAKE_ACCOUNT: abc12345.us-west-2.aws
✓ SNOWFLAKE_USER: your_username
✓ SNOWFLAKE_AUTHENTICATOR: PROGRAMMATIC_ACCESS_TOKEN
✓ SNOWFLAKE_PAT: SFZ...MGMz

✓ All required environment variables are set

================================================================================
 Step 2: Testing Snowflake Connection
================================================================================

✓ Connected to Snowflake (version: 8.51.0)
✓ Current user: YOUR_USERNAME
✓ Current account: ABC12345

[... continues with all setup steps ...]

================================================================================
 Setup Complete!
================================================================================

✅ Snowflake database initialized
✅ All tables created
✅ SuperScan workflow tested successfully
```

## Step 4: Verify Data in Snowflake UI

1. **Open Snowflake UI**
   - Go to: `https://<your_account>.snowflakecomputing.com`

2. **Navigate to Worksheets**
   - Click **Worksheets** in left navigation
   - Click **+ Worksheet** to create new worksheet

3. **Run verification queries:**
   ```sql
   -- Set context
   USE DATABASE superscan;
   USE SCHEMA public;
   
   -- Show all tables
   SHOW TABLES;
   
   -- Count rows
   SELECT 
       'projects' as table_name, COUNT(*) as rows FROM projects
   UNION ALL
   SELECT 'file_records', COUNT(*) FROM file_records
   UNION ALL
   SELECT 'ontology_proposals', COUNT(*) FROM ontology_proposals
   UNION ALL
   SELECT 'schemas', COUNT(*) FROM schemas
   UNION ALL
   SELECT 'nodes', COUNT(*) FROM nodes
   UNION ALL
   SELECT 'edges', COUNT(*) FROM edges;
   
   -- View project
   SELECT * FROM projects;
   
   -- View schemas
   SELECT 
       schema_name,
       version,
       entity_type,
       is_active
   FROM schemas
   ORDER BY entity_type, schema_name;
   ```

4. **Expected Results:**
   - `projects`: 1 row (test project created by setup script)
   - `file_records`: 1 row (test document)
   - `ontology_proposals`: 1 row (generated ontology)
   - `schemas`: 2-3 rows (Author, Paper, AUTHORED schemas)
   - `nodes`: 0 rows (no actual data ingested yet)
   - `edges`: 0 rows (no relationships yet)

## Troubleshooting

### Issue: "Authentication Token Expired"

**Solution:**
1. Generate new PAT in Snowflake UI
2. Update `SNOWFLAKE_PAT` in `.env` file
3. Run setup script again

### Issue: "Object 'SUPERSCAN' does not exist"

**Solution:**
- The setup script should create the database automatically
- If it fails, manually create it:
  ```sql
  CREATE DATABASE IF NOT EXISTS superscan;
  USE DATABASE superscan;
  CREATE SCHEMA IF NOT EXISTS public;
  ```

### Issue: "Insufficient privileges"

**Solution:**
- Ensure your user has necessary permissions
- Try using ACCOUNTADMIN role:
  ```sql
  USE ROLE ACCOUNTADMIN;
  ```

### Issue: Connection timeout

**Check:**
- Network connectivity
- Snowflake account identifier is correct
- Firewall/VPN settings

### Issue: "DEEPSEEK_API_KEY not set"

**Note:**
- This is a warning, not an error
- The setup script will use mock data for the ontology
- To use actual LLM, add `DEEPSEEK_API_KEY` to `.env`

## Next Steps

After successful setup:

1. **Run full SuperScan demo with real PDF:**
   ```bash
   python notebooks/superscan_snowflake_demo.py
   ```

2. **View comprehensive data guide:**
   ```bash
   cat notes/snowflake-data-viewing-guide.md
   ```

3. **Read PAT authentication guide:**
   ```bash
   cat notes/decisions/snowflake-pat-authentication-guide.md
   ```

4. **Start building your knowledge graph:**
   - Upload PDFs
   - Generate ontologies
   - Extract entities
   - Build relationships

## Security Notes

### Never Commit Secrets

Ensure `.env` is in `.gitignore`:
```bash
# Check .gitignore
cat ../.gitignore | grep .env

# If not present, add it:
echo ".env" >> ../.gitignore
echo ".env.*" >> ../.gitignore
echo "!.env.example" >> ../.gitignore
```

### Rotate Tokens Regularly

- Set calendar reminder to rotate PAT every 90 days
- Revoke old tokens immediately after rotation

## Support

If you encounter issues:
1. Check Snowflake documentation: https://docs.snowflake.com
2. Review error messages carefully
3. Check Snowflake query history for failed queries
4. Verify environment variables are correctly set

---

**Setup Version**: 1.0  
**Last Updated**: 2025-10-15
