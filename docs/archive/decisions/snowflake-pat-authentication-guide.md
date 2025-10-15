# Snowflake Personal Access Token (PAT) Authentication Guide

## Overview

Personal Access Tokens (PAT) provide a secure, non-interactive authentication method for Snowflake connections, ideal for automated scripts, CI/CD pipelines, and notebook environments.

## Why Use PAT?

✅ **Secure** - No password storage in code or config files  
✅ **Revocable** - Can be revoked instantly from Snowflake UI  
✅ **Auditable** - Token usage is logged in Snowflake  
✅ **Non-interactive** - Works in automated environments (notebooks, scripts, CI/CD)  
✅ **Scoped** - Limited to specific user privileges  

## Generating a Personal Access Token

### Step 1: Access Snowflake UI

1. Log in to your Snowflake account via web browser
2. Navigate to: **Profile** → **Personal Access Tokens**
3. Click **"Generate New Token"**

### Step 2: Configure Token

- **Token Name**: Give it a descriptive name (e.g., `superscan-notebook-token`)
- **Expiration**: Set expiration policy (recommended: 90 days)
- **Description**: Document intended use (e.g., "SuperScan development")

### Step 3: Copy Token

⚠️ **IMPORTANT**: The token is shown **only once**. Copy it immediately and store securely.

```
Example Token: SFZMWGRhMjc0YmUtNDc4OC00MjQ1LWIzYzYtNzE5NzQ5MTk4MGMz...
```

## Configuration Methods

### Method 1: Environment Variables (.env file) ⭐ **RECOMMENDED**

Create `/Users/harshitchoudhary/Desktop/lyzr-hackathon/code/.env`:

```bash
# Snowflake Connection
SNOWFLAKE_ACCOUNT=abc12345.us-west-2.aws
SNOWFLAKE_USER=your_username
SNOWFLAKE_AUTHENTICATOR=PROGRAMMATIC_ACCESS_TOKEN
SNOWFLAKE_PAT=your_generated_token_here

# Database settings
SNOWFLAKE_DATABASE=superscan
SNOWFLAKE_SCHEMA=public
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_ROLE=ACCOUNTADMIN
```

**Load in Python:**

```python
from dotenv import load_dotenv
import os

load_dotenv()

connection_params = {
    "account": os.getenv("SNOWFLAKE_ACCOUNT"),
    "user": os.getenv("SNOWFLAKE_USER"),
    "authenticator": "PROGRAMMATIC_ACCESS_TOKEN",
    "token": os.getenv("SNOWFLAKE_PAT"),
    "database": os.getenv("SNOWFLAKE_DATABASE"),
    "schema": os.getenv("SNOWFLAKE_SCHEMA"),
    "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE"),
    "role": os.getenv("SNOWFLAKE_ROLE"),
}
```

### Method 2: Token File Path

Store token in a separate file:

```bash
# Create token file
echo "your_token_here" > ~/.snowflake/pat_token.txt
chmod 600 ~/.snowflake/pat_token.txt
```

**Configuration:**

```bash
SNOWFLAKE_AUTHENTICATOR=PROGRAMMATIC_ACCESS_TOKEN
SNOWFLAKE_TOKEN_FILE_PATH=/Users/harshitchoudhary/.snowflake/pat_token.txt
```

**Load in Python:**

```python
connection_params = {
    "account": os.getenv("SNOWFLAKE_ACCOUNT"),
    "user": os.getenv("SNOWFLAKE_USER"),
    "authenticator": "PROGRAMMATIC_ACCESS_TOKEN",
    "token_file_path": os.getenv("SNOWFLAKE_TOKEN_FILE_PATH"),
    # ... other params
}
```

### Method 3: Direct Configuration (Not Recommended)

For testing only:

```python
import snowflake.connector

conn = snowflake.connector.connect(
    account="abc12345.us-west-2.aws",
    user="your_username",
    authenticator="PROGRAMMATIC_ACCESS_TOKEN",
    token="your_token_here",
    database="superscan",
    schema="public",
    warehouse="COMPUTE_WH",
    role="ACCOUNTADMIN"
)
```

## SuperScan Integration

### Update `graph_rag/db/connection.py`

```python
import os
from dotenv import load_dotenv
from snowflake.connector import connect
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine

load_dotenv()

def get_snowflake_connection():
    """Create Snowflake connection using PAT authentication."""
    
    auth_method = os.getenv("SNOWFLAKE_AUTHENTICATOR", "SNOWFLAKE")
    
    conn_params = {
        "account": os.getenv("SNOWFLAKE_ACCOUNT"),
        "user": os.getenv("SNOWFLAKE_USER"),
        "authenticator": auth_method,
        "database": os.getenv("SNOWFLAKE_DATABASE", "superscan"),
        "schema": os.getenv("SNOWFLAKE_SCHEMA", "public"),
        "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH"),
        "role": os.getenv("SNOWFLAKE_ROLE", "ACCOUNTADMIN"),
    }
    
    # Add authentication credential based on method
    if auth_method == "PROGRAMMATIC_ACCESS_TOKEN":
        token = os.getenv("SNOWFLAKE_PAT")
        token_file = os.getenv("SNOWFLAKE_TOKEN_FILE_PATH")
        
        if token:
            conn_params["token"] = token
        elif token_file:
            conn_params["token_file_path"] = token_file
        else:
            raise ValueError("PAT authentication requires SNOWFLAKE_PAT or SNOWFLAKE_TOKEN_FILE_PATH")
    
    elif auth_method == "SNOWFLAKE":
        password = os.getenv("SNOWFLAKE_PASSWORD")
        if not password:
            raise ValueError("Password authentication requires SNOWFLAKE_PASSWORD")
        conn_params["password"] = password
    
    return connect(**conn_params)

def get_sqlalchemy_engine():
    """Create SQLAlchemy engine for Snowflake with PAT support."""
    
    auth_method = os.getenv("SNOWFLAKE_AUTHENTICATOR", "SNOWFLAKE")
    account = os.getenv("SNOWFLAKE_ACCOUNT")
    user = os.getenv("SNOWFLAKE_USER")
    database = os.getenv("SNOWFLAKE_DATABASE", "superscan")
    schema = os.getenv("SNOWFLAKE_SCHEMA", "public")
    warehouse = os.getenv("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH")
    role = os.getenv("SNOWFLAKE_ROLE", "ACCOUNTADMIN")
    
    if auth_method == "PROGRAMMATIC_ACCESS_TOKEN":
        token = os.getenv("SNOWFLAKE_PAT")
        if not token:
            raise ValueError("PAT authentication requires SNOWFLAKE_PAT")
        
        # URL encode the token for SQLAlchemy
        from urllib.parse import quote_plus
        encoded_token = quote_plus(token)
        
        connection_string = (
            f"snowflake://{user}@{account}/"
            f"{database}/{schema}"
            f"?authenticator=PROGRAMMATIC_ACCESS_TOKEN"
            f"&token={encoded_token}"
            f"&warehouse={warehouse}"
            f"&role={role}"
        )
    else:
        password = os.getenv("SNOWFLAKE_PASSWORD")
        if not password:
            raise ValueError("Password authentication requires SNOWFLAKE_PASSWORD")
        
        from urllib.parse import quote_plus
        encoded_password = quote_plus(password)
        
        connection_string = (
            f"snowflake://{user}:{encoded_password}@{account}/"
            f"{database}/{schema}"
            f"?warehouse={warehouse}"
            f"&role={role}"
        )
    
    return create_engine(connection_string)
```

## Security Best Practices

### 1. Never Commit Tokens to Git

Add to `.gitignore`:

```
.env
.env.*
!.env.example
*.token
*_token.txt
```

### 2. Rotate Tokens Regularly

- Set expiration dates on tokens (e.g., 90 days)
- Create calendar reminders to rotate before expiration
- Revoke old tokens immediately after rotation

### 3. Use Separate Tokens per Environment

```bash
# Development
SNOWFLAKE_PAT=dev_token_here

# Staging
SNOWFLAKE_PAT=staging_token_here

# Production
SNOWFLAKE_PAT=prod_token_here
```

### 4. Minimal Privilege Principle

- Create service users with limited roles
- Grant only necessary permissions
- Use warehouse-specific roles

### 5. Monitor Token Usage

Check Snowflake query history:

```sql
-- View token usage
SELECT 
    user_name,
    client_application_id,
    query_text,
    start_time,
    execution_status
FROM snowflake.account_usage.query_history
WHERE authentication_method = 'PROGRAMMATIC_ACCESS_TOKEN'
ORDER BY start_time DESC
LIMIT 100;
```

## Troubleshooting

### Error: "Authentication Token Expired"

**Solution**: Generate a new token and update `.env`

### Error: "Invalid Token"

**Causes**:
- Token copied incorrectly (check for extra spaces/newlines)
- Token has been revoked
- Token belongs to different account

**Solution**: Re-generate token and verify account details

### Error: "Insufficient Privileges"

**Solution**: Ensure user has required role/permissions:

```sql
-- Grant necessary privileges
GRANT ROLE SYSADMIN TO USER your_username;
GRANT USAGE ON WAREHOUSE COMPUTE_WH TO ROLE your_role;
```

### Connection Times Out

**Check**:
- Network connectivity
- Snowflake account region matches `.env`
- Firewall/proxy settings

## Viewing Data in Snowflake UI

### Using SQL Worksheets

1. Navigate to **Worksheets** in Snowflake UI
2. Select warehouse: `COMPUTE_WH`
3. Run queries:

```sql
-- Set context
USE DATABASE superscan;
USE SCHEMA public;

-- List all tables
SHOW TABLES;

-- View projects
SELECT * FROM projects;

-- View schemas
SELECT 
    id,
    schema_name,
    version,
    entity_type,
    structured_attributes
FROM schemas;

-- View nodes with parsed VARIANT data
SELECT 
    id,
    label,
    structured_data:name::STRING as name,
    structured_data:type::STRING as type
FROM nodes
LIMIT 10;
```

### Using Data Browser

1. Navigate to **Data** → **Databases**
2. Expand `SUPERSCAN` → `PUBLIC`
3. Click on table (e.g., `PROJECTS`)
4. Click **Data Preview**

## Managing Projects & Databases

### Create Database

```sql
CREATE DATABASE IF NOT EXISTS superscan;
USE DATABASE superscan;
CREATE SCHEMA IF NOT EXISTS public;
```

### Create Warehouse

```sql
CREATE WAREHOUSE IF NOT EXISTS compute_wh
    WAREHOUSE_SIZE = 'XSMALL'
    AUTO_SUSPEND = 300
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = TRUE;
```

### Grant Permissions

```sql
GRANT USAGE ON DATABASE superscan TO ROLE your_role;
GRANT USAGE ON SCHEMA superscan.public TO ROLE your_role;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA superscan.public TO ROLE your_role;
GRANT USAGE ON WAREHOUSE compute_wh TO ROLE your_role;
```

## Reference Links

- [Snowflake PAT Documentation](https://docs.snowflake.com/en/user-guide/security-programmatic-access-tokens)
- [Python Connector Docs](https://docs.snowflake.com/en/user-guide/python-connector)
- [SQLAlchemy Snowflake Dialect](https://docs.snowflake.com/en/user-guide/sqlalchemy)

---

**Document Version**: 1.0  
**Last Updated**: 2025-10-15  
**Author**: SuperScan Development Team
