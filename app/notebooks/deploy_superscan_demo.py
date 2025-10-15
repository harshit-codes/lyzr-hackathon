#!/usr/bin/env python3
"""
Deploy SuperScan Demo Notebook to Snowflake using PAT token authentication.
"""

import os
import sys
import snowflake.connector
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent.parent / '.env')

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
NOTEBOOK_FILE = "superscan_snowflake_demo.py"
NOTEBOOK_NAME = "SUPERSCAN_DEMO_NOTEBOOK"

def main():
    # Check for password or token
    if not SNOWFLAKE_PASSWORD and not SNOWFLAKE_TOKEN:
        print("❌ Error: Neither SNOWFLAKE_PASSWORD nor SNOWFLAKE_TOKEN found in .env file")
        sys.exit(1)
    
    auth_method = "password" if SNOWFLAKE_PASSWORD else "PAT token"
    print("=" * 70)
    print("DEPLOYING SUPERSCAN DEMO NOTEBOOK TO SNOWFLAKE")
    print("=" * 70)
    print(f"🔗 Account: {SNOWFLAKE_ACCOUNT}")
    print(f"👤 User: {SNOWFLAKE_USER}")
    print(f"🔐 Auth: {auth_method}")
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
        print(f"✅ Context: User={result[0]}, Role={result[1]}, Warehouse={result[2]}, DB={result[3]}")
        print()
        
        # Create stage if not exists
        print(f"📦 Creating/verifying stage: {STAGE_NAME}")
        cursor.execute(f"CREATE STAGE IF NOT EXISTS {STAGE_NAME}")
        print(f"✅ Stage ready")
        print()
        
        # Upload notebook file to stage
        print(f"📤 Uploading {NOTEBOOK_FILE} to stage...")
        notebook_path = Path(__file__).parent / NOTEBOOK_FILE
        if not notebook_path.exists():
            print(f"❌ Error: {NOTEBOOK_FILE} not found at {notebook_path}")
            sys.exit(1)
        
        cursor.execute(f"PUT file://{notebook_path} @{STAGE_NAME} AUTO_COMPRESS=FALSE OVERWRITE=TRUE")
        print(f"✅ Uploaded {NOTEBOOK_FILE}")
        print()
        
        # List files in stage to verify
        print(f"📋 Files in @{STAGE_NAME}:")
        cursor.execute(f"LIST @{STAGE_NAME}")
        for row in cursor.fetchall():
            filename = row[0].split('/')[-1]
            if 'superscan' in filename.lower():
                print(f"  ✓ {filename}")
        print()
        
        # Create notebook - Note: Snowflake notebooks typically use .ipynb format
        # But we can create a Python script notebook
        print(f"📓 Creating Snowflake Notebook: {NOTEBOOK_NAME}")
        
        # First, check if we need to convert .py to .ipynb
        # For now, let's try to create it directly as a Python notebook
        # Snowflake may require .ipynb format, so we'll note that
        
        try:
            create_notebook_sql = f"""
            CREATE OR REPLACE NOTEBOOK {SNOWFLAKE_DATABASE}.{SNOWFLAKE_SCHEMA}.{NOTEBOOK_NAME}
            FROM '@{STAGE_NAME}'
            MAIN_FILE = '{NOTEBOOK_FILE}'
            QUERY_WAREHOUSE = '{SNOWFLAKE_WAREHOUSE}'
            """
            cursor.execute(create_notebook_sql)
            print(f"✅ Notebook created: {NOTEBOOK_NAME}")
        except Exception as e:
            print(f"⚠️  Note: Snowflake notebooks may require .ipynb format")
            print(f"   Error: {e}")
            print()
            print("💡 Alternative: The Python script has been uploaded to the stage.")
            print("   You can:")
            print("   1. Download it from the stage")
            print("   2. Convert to .ipynb format (Jupyter notebook)")
            print("   3. Re-upload and create notebook")
            print()
            print("   Or use the Python script directly in Snowpark/Streamlit")
        
        print()
        
        # Get notebook URL
        account_parts = SNOWFLAKE_ACCOUNT.split('-')
        org_id = account_parts[0].lower()
        account_id = account_parts[1].lower()
        notebook_url = f"https://app.snowflake.com/{org_id}/{account_id}/#/notebooks/{SNOWFLAKE_DATABASE}.{SNOWFLAKE_SCHEMA}.{NOTEBOOK_NAME}"
        
        print("=" * 70)
        print("🎉 DEPLOYMENT COMPLETE!")
        print("=" * 70)
        print()
        print(f"📋 Summary:")
        print(f"  - File uploaded to: @{STAGE_NAME}/{NOTEBOOK_FILE}")
        print(f"  - Notebook name: {NOTEBOOK_NAME}")
        print(f"  - Database: {SNOWFLAKE_DATABASE}.{SNOWFLAKE_SCHEMA}")
        print()
        print(f"🔗 Access notebook at:")
        print(f"   {notebook_url}")
        print()
        print(f"   Or navigate to: Snowflake UI → Projects → Notebooks → {NOTEBOOK_NAME}")
        print()
        print("=" * 70)
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
