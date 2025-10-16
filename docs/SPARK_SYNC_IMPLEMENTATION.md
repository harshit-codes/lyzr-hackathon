# Implementing Neo4j-Snowflake Spark Integration

## Step 1: Set Up Spark Environment

### Option A: Local Spark Setup (Development)
```bash
# Install Spark
brew install apache-spark

# Download Neo4j Spark Connector
# From: https://neo4j.com/docs/spark/current/
wget https://repo1.maven.org/maven2/org/neo4j/neo4j-connector-apache-spark_2.12/5.3.0/neo4j-connector-apache-spark_2.12-5.3.0.jar

# Download Snowflake Spark Connector
wget https://repo1.maven.org/maven2/net/snowflake/spark-snowflake_2.12/2.11.0-spark_3.3/spark-snowflake_2.12-2.11.0-spark_3.3.jar
```

### Option B: Databricks (Production)
- Use Databricks workspace for managed Spark
- Install Neo4j and Snowflake connectors via cluster libraries

## Step 2: Create Spark Sync Job

### Python Implementation
```python
from pyspark.sql import SparkSession
import os

# Initialize Spark with connectors
spark = SparkSession.builder \
    .appName("Neo4j-Snowflake-Sync") \
    .config("spark.jars", "/path/to/neo4j-connector.jar,/path/to/snowflake-connector.jar") \
    .getOrCreate()

# Configuration
neo4j_config = {
    "url": os.getenv("NEO4J_URI"),
    "user": os.getenv("NEO4J_USER"),
    "password": os.getenv("NEO4J_PASSWORD")
}

snowflake_config = {
    "sfURL": f"{os.getenv('SNOWFLAKE_ACCOUNT')}.snowflakecomputing.com",
    "sfUser": os.getenv("SNOWFLAKE_USER"),
    "sfPassword": os.getenv("SNOWFLAKE_PASSWORD"),
    "sfDatabase": os.getenv("SNOWFLAKE_DATABASE"),
    "sfSchema": os.getenv("SNOWFLAKE_SCHEMA"),
    "sfWarehouse": os.getenv("SNOWFLAKE_WAREHOUSE")
}

def sync_entities_to_snowflake():
    """Sync Neo4j entities to Snowflake tables"""

    # Load entities from Neo4j
    entities_df = spark.read.format("org.neo4j.spark.DataSource") \
        .option("url", neo4j_config["url"]) \
        .option("authentication.basic.username", neo4j_config["user"]) \
        .option("authentication.basic.password", neo4j_config["password"]) \
        .option("labels", ":Entity") \
        .load()

    # Save to Snowflake
    entities_df.write \
        .format("snowflake") \
        .options(**snowflake_config) \
        .option("dbtable", "SUPERSUITE_ENTITIES") \
        .mode("overwrite") \
        .save()

def sync_relationships_to_snowflake():
    """Sync Neo4j relationships to Snowflake tables"""

    # Load relationships from Neo4j
    relationships_df = spark.read.format("org.neo4j.spark.DataSource") \
        .option("url", neo4j_config["url"]) \
        .option("authentication.basic.username", neo4j_config["user"]) \
        .option("authentication.basic.password", neo4j_config["password"]) \
        .option("relationship", "RELATED_TO") \
        .option("relationship.nodes.map", "true") \
        .load()

    # Save to Snowflake
    relationships_df.write \
        .format("snowflake") \
        .options(**snowflake_config) \
        .option("dbtable", "SUPERSUITE_RELATIONSHIPS") \
        .mode("overwrite") \
        .save()

def sync_chunks_to_snowflake():
    """Sync document chunks and embeddings"""

    # Load chunks from Neo4j
    chunks_df = spark.read.format("org.neo4j.spark.DataSource") \
        .option("url", neo4j_config["url"]) \
        .option("authentication.basic.username", neo4j_config["user"]) \
        .option("authentication.basic.password", neo4j_config["password"]) \
        .option("labels", ":Chunk") \
        .load()

    # Save to Snowflake
    chunks_df.write \
        .format("snowflake") \
        .options(**snowflake_config) \
        .option("dbtable", "SUPERSUITE_CHUNKS") \
        .mode("overwrite") \
        .save()

if __name__ == "__main__":
    sync_entities_to_snowflake()
    sync_relationships_to_snowflake()
    sync_chunks_to_snowflake()
    print("✅ Neo4j to Snowflake sync complete")
```

## Step 3: Schedule Sync Jobs

### Using Cron (Simple)
```bash
# Add to crontab for hourly sync
0 * * * * /path/to/spark-submit /path/to/sync_job.py
```

### Using Apache Airflow (Production)
```python
from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'superset',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'neo4j_snowflake_sync',
    default_args=default_args,
    description='Sync Neo4j graph data to Snowflake',
    schedule_interval=timedelta(hours=1),
    catchup=False
)

sync_task = BashOperator(
    task_id='run_sync',
    bash_command='spark-submit /path/to/sync_job.py',
    dag=dag
)
```

## Step 4: Update SuperSuite to Use Synced Data

### Modify EndToEndOrchestrator
```python
class EndToEndOrchestrator:
    def __init__(self, use_synced_graph=True):
        self.use_synced_graph = use_synced_graph
        # ... existing init code ...

    def query_knowledge_base(self, query: str):
        if self.use_synced_graph:
            # Use Snowflake tables for graph queries
            return self._query_synced_graph(query)
        else:
            # Use real Neo4j for complex graph operations
            return self._query_neo4j_graph(query)

    def _query_synced_graph(self, query: str):
        """Query using synced data in Snowflake"""
        # Implement SQL-based graph queries using synced tables
        # This would use CTEs and recursive queries for graph traversal
        pass
```

## Step 5: Update Streamlit App

### Add Sync Status Display
```python
def display_sync_status():
    """Show when graph data was last synced"""
    try:
        # Query Snowflake for last sync timestamp
        sync_status = get_sync_status_from_snowflake()
        st.info(f"📊 Graph data last synced: {sync_status['last_sync']}")
    except:
        st.warning("⚠️ Graph data sync status unavailable")
```

## Benefits of This Approach

1. **Graph Data Available**: Entity and relationship data accessible in Snowflake
2. **SQL Analytics**: Use Snowflake's analytical capabilities on graph data
3. **Scalable**: Snowflake can handle large graph datasets
4. **Cost Effective**: No need for separate Neo4j infrastructure for read operations

## Limitations

1. **Not Real-time**: Data latency based on sync frequency
2. **Limited Graph Operations**: Complex graph algorithms harder in SQL
3. **Data Duplication**: Graph data stored in both Neo4j and Snowflake
4. **Sync Complexity**: Requires monitoring and error handling

## Recommended Sync Frequency

- **High-value data**: Every 15-30 minutes
- **Regular operations**: Hourly
- **Bulk operations**: Daily or weekly

This approach provides a **practical balance** between real-time graph capabilities and Snowflake integration.