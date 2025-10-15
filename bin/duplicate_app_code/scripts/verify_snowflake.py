#!/usr/bin/env python3
"""
Verify Snowflake Data

Quick script to check data in Snowflake tables.
"""

import os
import sys
from pathlib import Path

# Add code directory to path
CODE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(CODE_DIR))

from dotenv import load_dotenv
import snowflake.connector

load_dotenv()

def main():
    print("=" * 80)
    print(" Snowflake Data Verification")
    print("=" * 80)
    print()
    
    # Connect to Snowflake
    conn = snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE", "LYZRHACK"),
        schema=os.getenv("SNOWFLAKE_SCHEMA", "PUBLIC"),
    )
    
    cursor = conn.cursor()
    
    # Get row counts
    print("Row Counts:")
    print("-" * 80)
    tables = ["projects", "files", "ontology_proposals", "schemas", "nodes", "edges"]
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  {table:25} {count:>5} rows")
    
    print()
    
    # Show projects
    print("Projects:")
    print("-" * 80)
    cursor.execute("SELECT * FROM projects")
    cols = [desc[0] for desc in cursor.description]
    print(f"  Columns: {', '.join(cols)}")
    
    for row in cursor.fetchall():
        print(f"\n  Project ID: {row[0]}")
        print(f"  Name: {row[1]}")
        print(f"  Status: {row[2]}")
    
    print()
    
    # Show schemas
    print("Schemas:")
    print("-" * 80)
    cursor.execute("""
        SELECT SCHEMA_NAME, VERSION, ENTITY_TYPE, IS_ACTIVE 
        FROM schemas 
        ORDER BY ENTITY_TYPE, SCHEMA_NAME
    """)
    
    for row in cursor.fetchall():
        print(f"  {row[0]:20} v{row[1]:8} {row[2]:8} active={row[3]}")
    
    print()
    print("=" * 80)
    print(" ✓ Verification Complete")
    print("=" * 80)
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()
