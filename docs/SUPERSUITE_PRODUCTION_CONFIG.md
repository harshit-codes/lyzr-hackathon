# SuperSuite Production Configuration Guide

## Environment Variables Required for Real SuperSuite Components

### Snowflake Database (✅ Supported)
These are automatically detected by the DatabaseConfig class:
- `SNOWFLAKE_ACCOUNT` - Your Snowflake account identifier
- `SNOWFLAKE_USER` - Database username
- `SNOWFLAKE_PASSWORD` - Database password
- `SNOWFLAKE_DATABASE` - Target database name
- `SNOWFLAKE_WAREHOUSE` - Warehouse for compute resources
- `SNOWFLAKE_SCHEMA` - Schema name (optional, defaults to PUBLIC)

### Neo4j Graph Database (❌ Blocked in Snowflake Streamlit)
Required for full SuperSuite functionality:
- `NEO4J_URI` - Neo4j connection URI (e.g., bolt://your-instance:7687)
- `NEO4J_USER` - Neo4j username
- `NEO4J_PASSWORD` - Neo4j password

**Note**: External Neo4j connections are not allowed in Snowflake Streamlit apps due to security restrictions.

### AI Services (✅ Supported)
- `OPENAI_API_KEY` - Required for LLM-powered features
- `DEEPSEEK_API_KEY` - Optional, for alternative LLM provider

### Current Status

The app now attempts real SuperSuite initialization first, with graceful fallback to demo mode for unavailable services. This means:

1. **Database**: Will use real Snowflake connections ✅
2. **File Processing**: Will attempt real PDF processing ✅
3. **AI Features**: Will use real OpenAI API if key is provided ✅
4. **Graph Operations**: Will fail and fall back to demo mode ❌ (but Spark integration possible)

**New Finding**: Neo4j provides a Spark-based connector for batch data synchronization between Neo4j and Snowflake, offering a path to graph data integration without real-time connections.

## Implementation Options

### Option 1: Hybrid Mode (Recommended)
- Use real Snowflake database
- Use real file processing with stage storage
- Skip Neo4j graph operations (demo mode)
- Use real AI services

### Option 2: Full Real Mode (Requires External Hosting)
- Deploy SuperSuite components outside Snowflake
- Use Snowflake only for database and UI
- Connect via APIs to external SuperSuite services

### Option 3: Spark-Based Graph Integration (Advanced)
- **Neo4j Spark Connector**: Use scheduled Spark jobs to sync graph data between Neo4j and Snowflake
- **Batch Synchronization**: Periodic data transfer instead of real-time connections
- **Hybrid Architecture**: Real-time graph operations in Neo4j, analytical queries in Snowflake
- **Requirements**: Spark cluster, scheduling system, additional dependencies

**Pros**: Enables graph data access in Snowflake, maintains graph capabilities
**Cons**: Not real-time, requires additional infrastructure, more complex setup

### Option 4: External API Architecture (Recommended for Full Functionality)
- **Deploy SuperSuite Externally**: Host full SuperSuite outside Snowflake
- **API Integration**: Connect Snowflake Streamlit UI to external SuperSuite APIs
- **Real-time Graph Operations**: Full Neo4j functionality maintained
- **Database Sync**: Use Snowflake for primary data storage with API-driven operations

## Implementation Steps

### 1. Set Environment Variables
```bash
export SNOWFLAKE_ACCOUNT="your_account"
export SNOWFLAKE_USER="your_user"
export SNOWFLAKE_PASSWORD="your_password"
export SNOWFLAKE_DATABASE="SUPERSUITE"
export SNOWFLAKE_WAREHOUSE="your_warehouse"
export OPENAI_API_KEY="your_openai_key"
export NEO4J_URI="neo4j://your-neo4j-instance:7687"
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="your_neo4j_password"
```

### 2. Set Up Sync Infrastructure
```bash
# Install dependencies
pip install -r requirements-sync.txt

# Run complete setup
python scripts/setup_sync.py --all
```

### 3. Deploy Updated Streamlit App
The app now automatically detects Snowflake environment and uses synced graph data.

### 4. Schedule Regular Sync
```bash
# Option 1: Cron job (every 30 minutes)
*/30 * * * * cd /path/to/project && python scripts/sync_scheduler.py --once

# Option 2: Background process
python scripts/sync_scheduler.py --interval 1800 &
```