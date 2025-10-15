#!/usr/bin/env python3
"""
Deploy Snowflake Notebook using PAT token authentication.
This bypasses the Snowflake CLI authentication issues.
"""

import os
import sys
import snowflake.connector
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent.parent.parent / '.env')

# Snowflake connection parameters
SNOWFLAKE_ACCOUNT = os.getenv('SNOWFLAKE_ACCOUNT', 'FHWELTT-XS07400')
SNOWFLAKE_USER = os.getenv('SNOWFLAKE_USER', 'HARSHITCODES')
SNOWFLAKE_PASSWORD = os.getenv('SNOWFLAKE_PASSWORD')
SNOWFLAKE_TOKEN = os.getenv('SNOWFLAKE_TOKEN')
SNOWFLAKE_ROLE = os.getenv('SNOWFLAKE_ROLE', 'ACCOUNTADMIN')
SNOWFLAKE_WAREHOUSE = os.getenv('SNOWFLAKE_WAREHOUSE', 'COMPUTE_WH')
SNOWFLAKE_DATABASE = os.getenv('SNOWFLAKE_DATABASE', 'SNOWFLAKE_LEARNING_DB')
SNOWFLAKE_SCHEMA = os.getenv('SNOWFLAKE_SCHEMA', 'PUBLIC')

STAGE_NAME = f"{SNOWFLAKE_DATABASE}.{SNOWFLAKE_SCHEMA}.NOTEBOOKS_STAGE"
NOTEBOOK_FILE = "hello_world.ipynb"
NOTEBOOK_NAME = "HELLO_WORLD_NOTEBOOK"

def main():
    # Check for password or token
    if not SNOWFLAKE_PASSWORD and not SNOWFLAKE_TOKEN:
        print("❌ Error: Neither SNOWFLAKE_PASSWORD nor SNOWFLAKE_TOKEN found in .env file")
        sys.exit(1)
    
    auth_method = "password" if SNOWFLAKE_PASSWORD else "PAT token"
    print(f"🔗 Connecting to Snowflake account: {SNOWFLAKE_ACCOUNT}")
    print(f"👤 User: {SNOWFLAKE_USER}")
    print(f"🔐 Auth method: {auth_method}")
    print(f"🎭 Role: {SNOWFLAKE_ROLE}")
    print(f"🏠 Warehouse: {SNOWFLAKE_WAREHOUSE}")
    print(f"📊 Database: {SNOWFLAKE_DATABASE}.{SNOWFLAKE_SCHEMA}")
    print()
    
    try:
        # Connect using password (preferred) or PAT token
        if SNOWFLAKE_PASSWORD:
            conn = snowflake.connector.connect(
                account=SNOWFLAKE_ACCOUNT,
                user=SNOWFLAKE_USER,
                password=SNOWFLAKE_PASSWORD,
                role=SNOWFLAKE_ROLE,
                warehouse=SNOWFLAKE_WAREHOUSE,
                database=SNOWFLAKE_DATABASE,
                schema=SNOWFLAKE_SCHEMA
            )
        else:
            conn = snowflake.connector.connect(
                account=SNOWFLAKE_ACCOUNT,
                user=SNOWFLAKE_USER,
                token=SNOWFLAKE_TOKEN,
                authenticator='oauth',
                role=SNOWFLAKE_ROLE,
                warehouse=SNOWFLAKE_WAREHOUSE,
                database=SNOWFLAKE_DATABASE,
                schema=SNOWFLAKE_SCHEMA
            )
        
        print("✅ Connected to Snowflake successfully!")
        
        cursor = conn.cursor()
        
        # Test connection
        cursor.execute("SELECT CURRENT_USER(), CURRENT_ROLE(), CURRENT_WAREHOUSE(), CURRENT_DATABASE()")
        result = cursor.fetchone()
        print(f"✅ Current context: User={result[0]}, Role={result[1]}, Warehouse={result[2]}, Database={result[3]}")
        print()
        
        # Create stage if not exists
        print(f"📦 Creating stage: {STAGE_NAME}")
        cursor.execute(f"CREATE STAGE IF NOT EXISTS {STAGE_NAME}")
        print(f"✅ Stage created/verified: {STAGE_NAME}")
        print()
        
        # Upload notebook file to stage
        print(f"📤 Uploading {NOTEBOOK_FILE} to stage...")
        notebook_path = Path(__file__).parent / NOTEBOOK_FILE
        if not notebook_path.exists():
            print(f"❌ Error: {NOTEBOOK_FILE} not found at {notebook_path}")
            sys.exit(1)
        
        cursor.execute(f"PUT file://{notebook_path} @{STAGE_NAME} AUTO_COMPRESS=FALSE OVERWRITE=TRUE")
        print(f"✅ Uploaded {NOTEBOOK_FILE} to @{STAGE_NAME}")
        print()
        
        # List files in stage to verify
        print(f"📋 Files in @{STAGE_NAME}:")
        cursor.execute(f"LIST @{STAGE_NAME}")
        for row in cursor.fetchall():
            print(f"  - {row[0]}")
        print()
        
        # Create notebook
        print(f"📓 Creating Snowflake Notebook: {NOTEBOOK_NAME}")
        create_notebook_sql = f"""
        CREATE OR REPLACE NOTEBOOK {SNOWFLAKE_DATABASE}.{SNOWFLAKE_SCHEMA}.{NOTEBOOK_NAME}
        FROM '@{STAGE_NAME}'
        MAIN_FILE = '{NOTEBOOK_FILE}'
        QUERY_WAREHOUSE = '{SNOWFLAKE_WAREHOUSE}'
        """
        cursor.execute(create_notebook_sql)
        print(f"✅ Notebook created: {NOTEBOOK_NAME}")
        print()
        
        # Get notebook URL
        notebook_url = f"https://app.snowflake.com/{SNOWFLAKE_ACCOUNT.split('-')[0].lower()}/{SNOWFLAKE_ACCOUNT.split('-')[1].lower()}/#/notebooks/{SNOWFLAKE_DATABASE}.{SNOWFLAKE_SCHEMA}.{NOTEBOOK_NAME}"
        print(f"🎉 SUCCESS! Your notebook is deployed!")
        print(f"🔗 Access it at: {notebook_url}")
        print()
        print(f"Or navigate to: Snowflake UI → Projects → Notebooks → {NOTEBOOK_NAME}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
