#!/usr/bin/env python3
"""
Setup and Initialize Snowflake Database for SuperScan

This script:
1. Verifies Snowflake connection
2. Creates database and schema
3. Initializes all tables
4. Runs end-to-end SuperScan test
5. Verifies data was created

Usage:
    python scripts/setup_snowflake.py
"""

import sys
import os
from pathlib import Path
from uuid import UUID

# Add code directory to path
CODE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(CODE_DIR))

from dotenv import load_dotenv
import snowflake.connector
from snowflake.connector.errors import ProgrammingError

# Load environment variables
load_dotenv()

def print_section(title: str):
    """Print a section header."""
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80 + "\n")

def check_env_vars():
    """Check that required environment variables are set."""
    print_section("Step 1: Checking Environment Variables")
    
    required_vars = [
        "SNOWFLAKE_ACCOUNT",
        "SNOWFLAKE_USER",
        "SNOWFLAKE_AUTHENTICATOR",
    ]
    
    # Check authentication method
    auth_method = os.getenv("SNOWFLAKE_AUTHENTICATOR", "SNOWFLAKE")
    
    if auth_method == "PROGRAMMATIC_ACCESS_TOKEN":
        if not os.getenv("SNOWFLAKE_PAT") and not os.getenv("SNOWFLAKE_TOKEN_FILE_PATH"):
            print("❌ ERROR: PAT authentication requires either:")
            print("   - SNOWFLAKE_PAT environment variable")
            print("   - SNOWFLAKE_TOKEN_FILE_PATH environment variable")
            return False
    elif auth_method == "SNOWFLAKE":
        if not os.getenv("SNOWFLAKE_PASSWORD"):
            print("❌ ERROR: Password authentication requires SNOWFLAKE_PASSWORD")
            return False
    
    missing = []
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing.append(var)
        else:
            # Mask sensitive values
            if "PASSWORD" in var or "PAT" in var or "TOKEN" in var:
                display_value = value[:4] + "..." + value[-4:] if len(value) > 8 else "***"
            else:
                display_value = value
            print(f"✓ {var}: {display_value}")
    
    if missing:
        print(f"\n❌ ERROR: Missing required environment variables: {', '.join(missing)}")
        print("\nPlease create a .env file with the following variables:")
        print("  SNOWFLAKE_ACCOUNT=<your_account>")
        print("  SNOWFLAKE_USER=<your_user>")
        print("  SNOWFLAKE_AUTHENTICATOR=PROGRAMMATIC_ACCESS_TOKEN")
        print("  SNOWFLAKE_PAT=<your_token>")
        return False
    
    print("\n✓ All required environment variables are set")
    return True

def get_snowflake_connection():
    """Create a Snowflake connection."""
    auth_method = os.getenv("SNOWFLAKE_AUTHENTICATOR", "SNOWFLAKE")
    
    conn_params = {
        "account": os.getenv("SNOWFLAKE_ACCOUNT"),
        "user": os.getenv("SNOWFLAKE_USER"),
        "authenticator": auth_method,
    }
    
    # Add authentication credential
    if auth_method == "PROGRAMMATIC_ACCESS_TOKEN":
        token = os.getenv("SNOWFLAKE_PAT")
        token_file = os.getenv("SNOWFLAKE_TOKEN_FILE_PATH")
        if token:
            conn_params["token"] = token
        elif token_file:
            conn_params["token_file_path"] = token_file
    else:
        conn_params["password"] = os.getenv("SNOWFLAKE_PASSWORD")
    
    return snowflake.connector.connect(**conn_params)

def test_connection():
    """Test Snowflake connection."""
    print_section("Step 2: Testing Snowflake Connection")
    
    try:
        conn = get_snowflake_connection()
        cursor = conn.cursor()
        
        # Test query
        cursor.execute("SELECT CURRENT_VERSION()")
        version = cursor.fetchone()[0]
        print(f"✓ Connected to Snowflake (version: {version})")
        
        cursor.execute("SELECT CURRENT_USER()")
        user = cursor.fetchone()[0]
        print(f"✓ Current user: {user}")
        
        cursor.execute("SELECT CURRENT_ACCOUNT()")
        account = cursor.fetchone()[0]
        print(f"✓ Current account: {account}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def create_database_and_schema():
    """Create database and schema if they don't exist."""
    print_section("Step 3: Creating Database and Schema")
    
    try:
        conn = get_snowflake_connection()
        cursor = conn.cursor()
        
        # Get configuration from env
        warehouse = os.getenv("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH")
        database = os.getenv("SNOWFLAKE_DATABASE", "LYZRHACK")
        schema = os.getenv("SNOWFLAKE_SCHEMA", "PUBLIC")
        
        # Use warehouse
        cursor.execute(f"USE WAREHOUSE {warehouse}")
        print(f"✓ Using warehouse: {warehouse}")
        
        # Create database
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
        print(f"✓ Database '{database}' created (or already exists)")
        
        # Use database
        cursor.execute(f"USE DATABASE {database}")
        
        # Create schema
        cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")
        print(f"✓ Schema '{schema}' created (or already exists)")
        
        # Use schema
        cursor.execute(f"USE SCHEMA {schema}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Failed to create database/schema: {e}")
        return False

def initialize_tables():
    """Initialize all tables using SQLAlchemy."""
    print_section("Step 4: Initializing Tables")
    
    try:
        from graph_rag.db import init_database
        
        print("Calling init_database()...")
        init_database()
        
        print("\n✓ All tables initialized successfully")
        return True
        
    except Exception as e:
        print(f"❌ Failed to initialize tables: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_tables():
    """Verify that all tables were created."""
    print_section("Step 5: Verifying Tables")
    
    expected_tables = [
        "projects",
        "files",
        "ontology_proposals",
        "schemas",
        "nodes",
        "edges",
    ]
    
    try:
        conn = get_snowflake_connection()
        cursor = conn.cursor()
        
        # Get configuration from env
        database = os.getenv("SNOWFLAKE_DATABASE", "LYZRHACK")
        schema = os.getenv("SNOWFLAKE_SCHEMA", "PUBLIC")
        
        # Use database and schema
        cursor.execute(f"USE DATABASE {database}")
        cursor.execute(f"USE SCHEMA {schema}")
        
        # Get list of tables
        cursor.execute("SHOW TABLES")
        tables = [row[1].lower() for row in cursor.fetchall()]
        
        print("Found tables:")
        for table in tables:
            print(f"  - {table}")
        
        # Check all expected tables exist
        missing = [t for t in expected_tables if t not in tables]
        
        if missing:
            print(f"\n❌ Missing tables: {', '.join(missing)}")
            cursor.close()
            conn.close()
            return False
        
        print(f"\n✓ All {len(expected_tables)} tables created successfully")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Failed to verify tables: {e}")
        return False

def run_superscan_test():
    """Run end-to-end SuperScan test."""
    print_section("Step 6: Running SuperScan End-to-End Test")
    
    try:
        from uuid import UUID
        from graph_rag.db import get_db
        from superscan.project_service import ProjectService
        from superscan.file_service import FileService
        from superscan.schema_service import SchemaService
        from superscan.proposal_service import ProposalService
        from superscan.fast_scan import FastScan
        
        # Check for DeepSeek API key
        deepseek_key = os.getenv("DEEPSEEK_API_KEY")
        if not deepseek_key:
            print("⚠️  WARNING: DEEPSEEK_API_KEY not set. Using mock data.")
            use_llm = False
        else:
            print(f"✓ DeepSeek API key found: {deepseek_key[:8]}...")
            use_llm = True
        
        # Initialize services
        db = get_db()
        project_svc = ProjectService(db)
        file_svc = FileService(db)
        schema_svc = SchemaService(db)
        proposal_svc = ProposalService(db)
        
        # 1. Create project
        print("\n1. Creating project...")
        project_payload = {
            "project_name": "test-superscan-setup",
            "display_name": "SuperScan Setup Test",
            "owner_id": "setup-script",
            "tags": ["test", "setup"],
        }
        
        project = project_svc.create_project(project_payload)
        project_id = UUID(project["project_id"])
        print(f"   ✓ Project created: {project_id}")
        
        # 2. Upload file
        print("\n2. Uploading file metadata...")
        file_record = file_svc.upload_pdf(
            project_id=project_id,
            filename="test_document.pdf",
            size_bytes=1024000,
            pages=10,
            metadata={"source": "test", "topic": "graph RAG"},
        )
        file_id = file_record["file_id"]
        print(f"   ✓ File uploaded: {file_id}")
        
        # 3. Generate ontology proposal
        print("\n3. Generating ontology proposal...")
        
        if use_llm:
            # Use actual LLM
            text_snippets = [
                "This document describes a knowledge graph system for academic research.",
                "The system includes Authors, Papers, and Organizations as main entities.",
                "Authors write Papers and are affiliated with Organizations.",
            ]
            
            scanner = FastScan(
                api_key=deepseek_key,
                base_url="https://api.deepseek.com",
                model="deepseek-chat"
            )
            
            proposal_dict = scanner.generate_proposal(
                snippets=text_snippets,
                hints={"domain": "academic research, knowledge graphs"},
            )
        else:
            # Use mock data
            proposal_dict = {
                "summary": "Test ontology for knowledge graph system",
                "nodes": [
                    {
                        "schema_name": "Author",
                        "structured_attributes": [
                            {"name": "name", "data_type": "STRING", "required": True},
                            {"name": "email", "data_type": "STRING", "required": False},
                        ],
                    },
                    {
                        "schema_name": "Paper",
                        "structured_attributes": [
                            {"name": "title", "data_type": "STRING", "required": True},
                            {"name": "year", "data_type": "INTEGER", "required": False},
                        ],
                    },
                ],
                "edges": [
                    {
                        "schema_name": "AUTHORED",
                        "structured_attributes": [
                            {"name": "position", "data_type": "INTEGER", "required": False},
                        ],
                    },
                ],
            }
        
        print(f"   ✓ Generated {len(proposal_dict.get('nodes', []))} node types")
        print(f"   ✓ Generated {len(proposal_dict.get('edges', []))} edge types")
        
        # 4. Save proposal
        print("\n4. Saving proposal...")
        proposal = proposal_svc.create_proposal(
            project_id=project_id,
            nodes=proposal_dict.get("nodes", []),
            edges=proposal_dict.get("edges", []),
            source_files=[file_id],
            summary=proposal_dict.get("summary", "Test ontology"),
        )
        proposal_id = UUID(proposal["proposal_id"])
        print(f"   ✓ Proposal saved: {proposal_id}")
        
        # 5. Finalize proposal
        print("\n5. Finalizing proposal (creating schemas)...")
        result = proposal_svc.finalize_proposal(proposal_id)
        print(f"   ✓ Created {len(result['schemas'])} schemas")
        for schema in result["schemas"]:
            print(f"      - {schema['schema_name']} v{schema['version']} ({schema['entity_type']})")
        
        # 6. Verify data
        print("\n6. Verifying data...")
        schemas = schema_svc.list_schemas(project_id)
        print(f"   ✓ Found {schemas['total']} schema(s) in project")
        
        print("\n✓ SuperScan end-to-end test completed successfully!")
        return True, project_id
        
    except Exception as e:
        print(f"\n❌ SuperScan test failed: {e}")
        import traceback
        traceback.print_exc()
        return False, None

def query_data(project_id: UUID):
    """Query and display created data."""
    print_section("Step 7: Querying Created Data")
    
    try:
        conn = get_snowflake_connection()
        cursor = conn.cursor()
        
        database = os.getenv("SNOWFLAKE_DATABASE", "LYZRHACK")
        schema = os.getenv("SNOWFLAKE_SCHEMA", "PUBLIC")
        
        cursor.execute(f"USE DATABASE {database}")
        cursor.execute(f"USE SCHEMA {schema}")
        
        # Count rows in each table
        tables = ["projects", "files", "ontology_proposals", "schemas", "nodes", "edges"]
        
        print("Row counts:")
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  {table:25} {count:>5} rows")
        
        # Show project details
        print("\nProject details:")
        cursor.execute(f"SELECT id, name, status, owner_id FROM projects WHERE id = '{project_id}'")
        row = cursor.fetchone()
        if row:
            print(f"  ID:       {row[0]}")
            print(f"  Name:     {row[1]}")
            print(f"  Status:   {row[2]}")
            print(f"  Owner:    {row[3]}")
        
        # Show schemas
        print("\nSchemas in project:")
        cursor.execute(f"""
            SELECT schema_name, version, entity_type, is_active 
            FROM schemas 
            WHERE project_id = '{project_id}'
            ORDER BY entity_type, schema_name
        """)
        for row in cursor.fetchall():
            print(f"  {row[0]:15} v{row[1]}  {row[2]:8}  active={row[3]}")
        
        cursor.close()
        conn.close()
        
        print("\n✓ Data query completed")
        return True
        
    except Exception as e:
        print(f"❌ Failed to query data: {e}")
        return False

def main():
    """Main setup function."""
    print_section("SuperScan Snowflake Setup")
    print("This script will:")
    print("  1. Check environment variables")
    print("  2. Test Snowflake connection")
    print("  3. Create database and schema")
    print("  4. Initialize tables")
    print("  5. Verify tables")
    print("  6. Run SuperScan end-to-end test")
    print("  7. Query and display data")
    
    # Run setup steps
    if not check_env_vars():
        return 1
    
    if not test_connection():
        return 1
    
    if not create_database_and_schema():
        return 1
    
    if not initialize_tables():
        return 1
    
    if not verify_tables():
        return 1
    
    success, project_id = run_superscan_test()
    if not success:
        return 1
    
    if project_id and not query_data(project_id):
        return 1
    
    # Final summary
    print_section("Setup Complete!")
    print("✅ Snowflake database initialized")
    print("✅ All tables created")
    print("✅ SuperScan workflow tested successfully")
    print("\nNext steps:")
    print("  1. View data in Snowflake UI:")
    print("     https://<your_account>.snowflakecomputing.com")
    print("  2. Run queries in Worksheets:")
    print("     USE DATABASE superscan;")
    print("     USE SCHEMA public;")
    print("     SELECT * FROM projects;")
    print("  3. Check the data viewing guide:")
    print("     notes/snowflake-data-viewing-guide.md")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
