#!/bin/bash
"""
Setup script for configuring main Neo4j Aura and Snowflake instances for production testing.

This script helps you set up the required environment variables for running
remote production tests on your main cloud instances.
"""

echo "🚀 SuperSuite Production Environment Setup"
echo "=========================================="
echo ""

# Check if .env file exists
if [ -f ".env" ]; then
    echo "⚠️  .env file already exists. This script will append to it."
    echo "   Make sure to backup your existing .env file if needed."
    echo ""
fi

echo "📝 Please provide your main production instance credentials:"
echo ""

# Neo4j Aura Configuration
echo "🔗 Neo4j Aura Configuration:"
read -p "Neo4j Aura URI (e.g., neo4j+s://your-instance.databases.neo4j.io): " neo4j_uri
read -p "Neo4j Username (default: neo4j): " neo4j_user
neo4j_user=${neo4j_user:-neo4j}
read -s -p "Neo4j Password: " neo4j_password
echo ""

# Snowflake Configuration
echo ""
echo "❄️  Snowflake Configuration:"
read -p "Snowflake Account (e.g., your-account): " snowflake_account
read -p "Snowflake User: " snowflake_user
read -s -p "Snowflake Password: " snowflake_password
echo ""
read -p "Snowflake Database (default: SUPERSUITE_PROD): " snowflake_database
snowflake_database=${snowflake_database:-SUPERSUITE_PROD}
read -p "Snowflake Schema (default: PUBLIC): " snowflake_schema
snowflake_schema=${snowflake_schema:-PUBLIC}
read -p "Snowflake Warehouse: " snowflake_warehouse

# Graph API Configuration
echo ""
echo "🌐 Graph API Service Configuration:"
read -p "Graph API URL (e.g., https://your-api-service.com): " graph_api_url

# DeepSeek Configuration
echo ""
echo "🤖 DeepSeek Configuration:"
read -s -p "DeepSeek API Key: " deepseek_api_key
echo ""
read -p "DeepSeek Base URL (default: https://api.deepseek.com): " deepseek_base_url
deepseek_base_url=${deepseek_base_url:-https://api.deepseek.com}
read -p "DeepSeek Model (default: deepseek-chat): " deepseek_model
deepseek_model=${deepseek_model:-deepseek-chat}

# Write to .env file
echo ""
echo "📄 Writing configuration to .env file..."

cat >> .env << EOF

# Main Production Instances for Remote Testing
# ============================================

# Neo4j Aura (Main Production Instance)
TEST_NEO4J_URI=$neo4j_uri
TEST_NEO4J_USER=$neo4j_user
TEST_NEO4J_PASSWORD=$neo4j_password

# Snowflake (Main Production Instance)
TEST_SNOWFLAKE_ACCOUNT=$snowflake_account
TEST_SNOWFLAKE_USER=$snowflake_user
TEST_SNOWFLAKE_PASSWORD=$snowflake_password
TEST_SNOWFLAKE_DATABASE=$snowflake_database
TEST_SNOWFLAKE_SCHEMA=$snowflake_schema
TEST_SNOWFLAKE_WAREHOUSE=$snowflake_warehouse

# Graph API Service
TEST_GRAPH_API_URL=$graph_api_url

# DeepSeek API (for SuperSuite processing)
DEEPSEEK_API_KEY=$deepseek_api_key
DEEPSEEK_BASE_URL=$deepseek_base_url
DEEPSEEK_MODEL=$deepseek_model

# Local Development (can use same instances or different)
NEO4J_URI=$neo4j_uri
NEO4J_USER=$neo4j_user
NEO4J_PASSWORD=$neo4j_password

SNOWFLAKE_ACCOUNT=$snowflake_account
SNOWFLAKE_USER=$snowflake_user
SNOWFLAKE_PASSWORD=$snowflake_password
SNOWFLAKE_DATABASE=$snowflake_database
SNOWFLAKE_SCHEMA=$snowflake_schema
SNOWFLAKE_WAREHOUSE=$snowflake_warehouse

GRAPH_API_URL=$graph_api_url
EOF

echo ""
echo "✅ Configuration saved to .env file!"
echo ""
echo "🔧 Next steps:"
echo "1. Review the .env file to ensure all values are correct"
echo "2. Run: source .env"
echo "3. Execute remote production tests: python scripts/remote_production_test.py"
echo ""
echo "🧪 Test Commands:"
echo "  # Run all tests"
echo "  python scripts/remote_production_test.py"
echo ""
echo "  # Run specific test (e.g., Neo4j connection only)"
echo "  python -c \"from scripts.remote_production_test import RemoteProductionTester; t = RemoteProductionTester(); print(t.test_neo4j_connection())\""
echo ""
echo "📊 After testing, you can deploy to Snowflake Streamlit:"
echo "  snow streamlit deploy --env-file .env"