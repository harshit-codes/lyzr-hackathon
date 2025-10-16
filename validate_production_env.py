#!/usr/bin/env python3
"""
Quick environment validation script for production instances.

This script checks that all required environment variables are set
and validates basic connectivity to your main Neo4j Aura and Snowflake instances.
"""

import os
import sys
from typing import Dict, List, Tuple

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not available, rely on system environment

def check_environment_variables() -> Tuple[bool, List[str]]:
    """Check that all required environment variables are set."""
    required_vars = [
        ("NEO4J_URI", "Neo4j Aura instance URI"),
        ("NEO4J_USER", "Neo4j username"),
        ("NEO4J_PASSWORD", "Neo4j password"),
        ("SNOWFLAKE_ACCOUNT", "Snowflake account"),
        ("SNOWFLAKE_USER", "Snowflake username"),
        ("SNOWFLAKE_PASSWORD", "Snowflake password"),
        ("SNOWFLAKE_DATABASE", "Snowflake database"),
        ("SNOWFLAKE_SCHEMA", "Snowflake schema"),
        ("SNOWFLAKE_WAREHOUSE", "Snowflake warehouse"),
        ("DEEPSEEK_API_KEY", "DeepSeek API key")
    ]

    missing = []
    for var_name, description in required_vars:
        if not os.getenv(var_name):
            missing.append(f"{var_name} - {description}")

    return len(missing) == 0, missing

def test_neo4j_connection() -> bool:
    """Test basic Neo4j connection."""
    try:
        from neo4j import GraphDatabase

        uri = os.getenv("NEO4J_URI")
        user = os.getenv("NEO4J_USER")
        password = os.getenv("NEO4J_PASSWORD")

        driver = GraphDatabase.driver(uri, auth=(user, password))
        driver.verify_connectivity()

        with driver.session() as session:
            result = session.run("RETURN 'Neo4j connection successful' as message")
            record = result.single()
            message = record["message"]
            print(f"✅ Neo4j: {message}")

        driver.close()
        return True

    except Exception as e:
        print(f"❌ Neo4j connection failed: {e}")
        return False

def test_snowflake_connection() -> bool:
    """Test basic Snowflake connection."""
    try:
        import snowflake.connector

        account = os.getenv("SNOWFLAKE_ACCOUNT")
        user = os.getenv("SNOWFLAKE_USER")
        password = os.getenv("SNOWFLAKE_PASSWORD")
        database = os.getenv("SNOWFLAKE_DATABASE")
        schema = os.getenv("SNOWFLAKE_SCHEMA")
        warehouse = os.getenv("SNOWFLAKE_WAREHOUSE")

        conn = snowflake.connector.connect(
            account=account,
            user=user,
            password=password,
            database=database,
            schema=schema,
            warehouse=warehouse
        )

        cursor = conn.cursor()
        cursor.execute("SELECT CURRENT_ACCOUNT(), CURRENT_USER(), CURRENT_DATABASE()")
        result = cursor.fetchone()

        print(f"✅ Snowflake: Connected to {result[0]} as {result[1]} in {result[2]}")

        cursor.close()
        conn.close()
        return True

    except Exception as e:
        print(f"❌ Snowflake connection failed: {e}")
        return False

def test_deepseek_api() -> bool:
    """Test DeepSeek API connectivity."""
    try:
        import openai

        api_key = os.getenv("DEEPSEEK_API_KEY")
        base_url = os.getenv("DEEPSEEK_API_BASE_URL", "https://api.deepseek.com/v1")
        model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

        client = openai.OpenAI(api_key=api_key, base_url=base_url)

        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Hello, test message"}],
            max_tokens=10
        )

        print(f"✅ DeepSeek: API responding (model: {model})")
        return True

    except Exception as e:
        print(f"❌ DeepSeek API failed: {e}")
        return False

def main():
    """Main validation function."""
    print("🔍 SuperSuite Production Environment Validation")
    print("=" * 50)

    # Check environment variables
    print("\n📋 Checking environment variables...")
    env_ok, missing = check_environment_variables()

    if not env_ok:
        print("❌ Missing required environment variables:")
        for var in missing:
            print(f"   • {var}")
        print("\n💡 Run: bash setup_production_env.sh")
        return False

    print("✅ All required environment variables are set")

    # Test connections
    print("\n🔗 Testing connections...")

    neo4j_ok = test_neo4j_connection()
    snowflake_ok = test_snowflake_connection()
    deepseek_ok = test_deepseek_api()

    print("\n" + "=" * 50)
    if neo4j_ok and snowflake_ok and deepseek_ok:
        print("🎉 All validations passed! Ready for production testing.")
        print("\n🚀 Run remote tests:")
        print("   python scripts/remote_production_test.py")
        return True
    else:
        print("⚠️  Some validations failed. Please check your configuration.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)