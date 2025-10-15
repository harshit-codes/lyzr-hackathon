"""
Fix Snowflake SCHEMAS table ENTITY_TYPE column length issue.

This script alters the ENTITY_TYPE column to VARCHAR(255) to support
longer entity type names like 'Person', 'Organization', etc.
"""

import os
from dotenv import load_dotenv
import snowflake.connector

# Load environment
load_dotenv()

def fix_schemas_table():
    """Fix the SCHEMAS table ENTITY_TYPE column length."""
    
    print("=" * 80)
    print("Snowflake Schema Fix - ENTITY_TYPE Column")
    print("=" * 80)
    print()
    
    # Connect to Snowflake
    print("Connecting to Snowflake...")
    conn = snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA", "PUBLIC"),
        role=os.getenv("SNOWFLAKE_ROLE")
    )
    
    cursor = conn.cursor()
    
    try:
        # Check current column definition
        print("Checking current SCHEMAS table structure...")
        cursor.execute("""
            DESCRIBE TABLE SCHEMAS
        """)
        
        columns = cursor.fetchall()
        entity_type_col = [col for col in columns if col[0] == 'ENTITY_TYPE']
        
        if entity_type_col:
            print(f"Current ENTITY_TYPE column: {entity_type_col[0]}")
            print()
        
        # Alter the column
        print("Altering ENTITY_TYPE column to VARCHAR(255)...")
        cursor.execute("""
            ALTER TABLE SCHEMAS 
            MODIFY COLUMN ENTITY_TYPE VARCHAR(255)
        """)
        
        print("✓ Column altered successfully!")
        print()
        
        # Verify the change
        print("Verifying column change...")
        cursor.execute("""
            DESCRIBE TABLE SCHEMAS
        """)
        
        columns = cursor.fetchall()
        entity_type_col = [col for col in columns if col[0] == 'ENTITY_TYPE']
        
        if entity_type_col:
            print(f"Updated ENTITY_TYPE column: {entity_type_col[0]}")
            print()
        
        print("=" * 80)
        print("✅ Schema fix completed successfully!")
        print("=" * 80)
        print()
        print("You can now run: python test_superkb_e2e.py")
        print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print()
        print("If the column doesn't exist, the table may need to be recreated.")
        print("Check if SCHEMAS table exists with: SELECT * FROM SCHEMAS LIMIT 1;")
        
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    try:
        fix_schemas_table()
    except Exception as e:
        print()
        print("=" * 80)
        print(f"❌ FAILED: {e}")
        print("=" * 80)
        import traceback
        traceback.print_exc()
