#!/usr/bin/env python3
"""
Neo4j to Snowflake Graph Data Sync Job
Synchronizes graph data between Neo4j and Snowflake using Apache Spark

This job enables bidirectional synchronization:
- Neo4j → Snowflake: Graph data for analytics and Streamlit queries
- Snowflake → Neo4j: Relational data for graph enrichment

Supports dynamic schema creation based on SuperSuite processing results.
"""

import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Neo4jSnowflakeSync:
    """Handles bidirectional synchronization between Neo4j and Snowflake via Spark"""

    def __init__(self):
        self.spark = None
        self.neo4j_config = self._get_neo4j_config()
        self.snowflake_config = self._get_snowflake_config()

    def _get_neo4j_config(self) -> Dict[str, str]:
        """Get Neo4j connection configuration"""
        return {
            "url": os.getenv("NEO4J_URI", "neo4j://localhost:7687"),
            "user": os.getenv("NEO4J_USER", "neo4j"),
            "password": os.getenv("NEO4J_PASSWORD", "password")
        }

    def _get_snowflake_config(self) -> Dict[str, str]:
        """Get Snowflake connection configuration"""
        account = os.getenv("SNOWFLAKE_ACCOUNT")
        if not account:
            raise ValueError("SNOWFLAKE_ACCOUNT environment variable is required")

        return {
            "sfURL": f"{account}.snowflakecomputing.com",
            "sfUser": os.getenv("SNOWFLAKE_USER"),
            "sfPassword": os.getenv("SNOWFLAKE_PASSWORD"),
            "sfDatabase": os.getenv("SNOWFLAKE_DATABASE", "SUPERSUITE"),
            "sfSchema": os.getenv("SNOWFLAKE_SCHEMA", "PUBLIC"),
            "sfWarehouse": os.getenv("SNOWFLAKE_WAREHOUSE")
        }

    def initialize_spark(self):
        """Initialize Spark session with Neo4j and Snowflake connectors"""
        try:
            from pyspark.sql import SparkSession

            # Build Spark session with required packages
            spark_builder = SparkSession.builder \
                .appName("Neo4j-Snowflake-Bidirectional-Sync") \
                .config("spark.sql.adaptive.enabled", "true") \
                .config("spark.sql.adaptive.coalescePartitions.enabled", "true")

            # Add Neo4j connector
            neo4j_version = "5.3.0"
            spark_builder = spark_builder.config(
                "spark.jars.packages",
                f"org.neo4j:neo4j-connector-apache-spark_2.12:{neo4j_version}"
            )

            # Add Snowflake connector
            snowflake_version = "2.11.0-spark_3.3"
            spark_builder = spark_builder.config(
                "spark.jars.packages",
                f"net.snowflake:spark-snowflake_2.12:{snowflake_version}," +
                "net.snowflake:snowflake-jdbc:3.13.29"
            )

            self.spark = spark_builder.getOrCreate()
            logger.info("✅ Spark session initialized successfully")

        except ImportError as e:
            logger.error(f"❌ Failed to import Spark: {e}")
            logger.error("Please install PySpark: pip install pyspark")
            raise
        except Exception as e:
            logger.error(f"❌ Failed to initialize Spark: {e}")
            raise

import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Neo4jSnowflakeSync:
    """Handles synchronization of graph data from Neo4j to Snowflake via Spark"""

    def __init__(self):
        self.spark = None
        self.neo4j_config = self._get_neo4j_config()
        self.snowflake_config = self._get_snowflake_config()

    def _get_neo4j_config(self) -> Dict[str, str]:
        """Get Neo4j connection configuration"""
        return {
            "url": os.getenv("NEO4J_URI", "neo4j://localhost:7687"),
            "user": os.getenv("NEO4J_USER", "neo4j"),
            "password": os.getenv("NEO4J_PASSWORD", "password")
        }

    def _get_snowflake_config(self) -> Dict[str, str]:
        """Get Snowflake connection configuration"""
        account = os.getenv("SNOWFLAKE_ACCOUNT")
        if not account:
            raise ValueError("SNOWFLAKE_ACCOUNT environment variable is required")

        return {
            "sfURL": f"{account}.snowflakecomputing.com",
            "sfUser": os.getenv("SNOWFLAKE_USER"),
            "sfPassword": os.getenv("SNOWFLAKE_PASSWORD"),
            "sfDatabase": os.getenv("SNOWFLAKE_DATABASE", "SUPERSUITE"),
            "sfSchema": os.getenv("SNOWFLAKE_SCHEMA", "PUBLIC"),
            "sfWarehouse": os.getenv("SNOWFLAKE_WAREHOUSE")
        }

    def initialize_spark(self):
        """Initialize Spark session with Neo4j and Snowflake connectors"""
        try:
            from pyspark.sql import SparkSession

            # Build Spark session with required packages
            spark_builder = SparkSession.builder \
                .appName("Neo4j-Snowflake-Sync") \
                .config("spark.sql.adaptive.enabled", "true") \
                .config("spark.sql.adaptive.coalescePartitions.enabled", "true")

            # Add Neo4j connector
            neo4j_version = "5.3.0"
            spark_builder = spark_builder.config(
                "spark.jars.packages",
                f"org.neo4j:neo4j-connector-apache-spark_2.12:{neo4j_version}"
            )

            # Add Snowflake connector
            snowflake_version = "2.11.0-spark_3.3"
            spark_builder = spark_builder.config(
                "spark.jars.packages",
                f"net.snowflake:spark-snowflake_2.12:{snowflake_version}," +
                "net.snowflake:snowflake-jdbc:3.13.29"
            )

            self.spark = spark_builder.getOrCreate()
            logger.info("✅ Spark session initialized successfully")

        except ImportError as e:
            logger.error(f"❌ Failed to import Spark: {e}")
            logger.error("Please install PySpark: pip install pyspark")
            raise
        except Exception as e:
            logger.error(f"❌ Failed to initialize Spark: {e}")
            raise

    def sync_entities(self) -> int:
        """Sync entity nodes from Neo4j to Snowflake"""
        logger.info("🔄 Syncing entities from Neo4j to Snowflake...")

        try:
            # Load entities from Neo4j
            entities_df = self.spark.read.format("org.neo4j.spark.DataSource") \
                .option("url", self.neo4j_config["url"]) \
                .option("authentication.basic.username", self.neo4j_config["user"]) \
                .option("authentication.basic.password", self.neo4j_config["password"]) \
                .option("labels", ":Entity") \
                .load()

            entity_count = entities_df.count()
            logger.info(f"📊 Found {entity_count} entities in Neo4j")

            if entity_count > 0:
                # Add sync metadata
                from pyspark.sql.functions import current_timestamp, lit
                entities_df = entities_df.withColumn("last_synced", current_timestamp())
                entities_df = entities_df.withColumn("sync_source", lit("neo4j_spark_sync"))

                # Save to Snowflake
                entities_df.write \
                    .format("snowflake") \
                    .options(**self.snowflake_config) \
                    .option("dbtable", "SUPERSUITE_ENTITIES") \
                    .mode("overwrite") \
                    .save()

                logger.info(f"✅ Synced {entity_count} entities to Snowflake")
            else:
                logger.warning("⚠️ No entities found to sync")

            return entity_count

        except Exception as e:
            logger.error(f"❌ Failed to sync entities: {e}")
            raise

    def sync_relationships(self) -> int:
        """Sync relationships from Neo4j to Snowflake"""
        logger.info("🔄 Syncing relationships from Neo4j to Snowflake...")

        try:
            # Load relationships from Neo4j
            relationships_df = self.spark.read.format("org.neo4j.spark.DataSource") \
                .option("url", self.neo4j_config["url"]) \
                .option("authentication.basic.username", self.neo4j_config["user"]) \
                .option("authentication.basic.password", self.neo4j_config["password"]) \
                .option("relationship", "RELATED_TO") \
                .option("relationship.nodes.map", "true") \
                .option("relationship.source.labels", ":Entity") \
                .option("relationship.target.labels", ":Entity") \
                .load()

            relationship_count = relationships_df.count()
            logger.info(f"📊 Found {relationship_count} relationships in Neo4j")

            if relationship_count > 0:
                # Add sync metadata
                from pyspark.sql.functions import current_timestamp, lit
                relationships_df = relationships_df.withColumn("last_synced", current_timestamp())
                relationships_df = relationships_df.withColumn("sync_source", lit("neo4j_spark_sync"))

                # Save to Snowflake
                relationships_df.write \
                    .format("snowflake") \
                    .options(**self.snowflake_config) \
                    .option("dbtable", "SUPERSUITE_RELATIONSHIPS") \
                    .mode("overwrite") \
                    .save()

                logger.info(f"✅ Synced {relationship_count} relationships to Snowflake")
            else:
                logger.warning("⚠️ No relationships found to sync")

            return relationship_count

        except Exception as e:
            logger.error(f"❌ Failed to sync relationships: {e}")
            raise

    def sync_document_chunks(self) -> int:
        """Sync document chunks from Neo4j to Snowflake"""
        logger.info("🔄 Syncing document chunks from Neo4j to Snowflake...")

        try:
            # Load chunks from Neo4j
            chunks_df = self.spark.read.format("org.neo4j.spark.DataSource") \
                .option("url", self.neo4j_config["url"]) \
                .option("authentication.basic.username", self.neo4j_config["user"]) \
                .option("authentication.basic.password", self.neo4j_config["password"]) \
                .option("labels", ":Chunk") \
                .load()

            chunk_count = chunks_df.count()
            logger.info(f"📊 Found {chunk_count} document chunks in Neo4j")

            if chunk_count > 0:
                # Add sync metadata
                from pyspark.sql.functions import current_timestamp, lit
                chunks_df = chunks_df.withColumn("last_synced", current_timestamp())
                chunks_df = chunks_df.withColumn("sync_source", lit("neo4j_spark_sync"))

                # Save to Snowflake
                chunks_df.write \
                    .format("snowflake") \
                    .options(**self.snowflake_config) \
                    .option("dbtable", "SUPERSUITE_CHUNKS") \
                    .mode("overwrite") \
                    .save()

                logger.info(f"✅ Synced {chunk_count} chunks to Snowflake")
            else:
                logger.warning("⚠️ No chunks found to sync")

            return chunk_count

        except Exception as e:
            logger.error(f"❌ Failed to sync chunks: {e}")
            raise

    def sync_snowflake_to_neo4j(self) -> int:
        """Sync relational data from Snowflake to Neo4j for graph enrichment"""
        logger.info("🔄 Syncing relational data from Snowflake to Neo4j...")

        try:
            # Read SuperSuite relational data from Snowflake
            tables_to_sync = [
                "projects", "files", "schemas", "nodes", "edges", "chunks"
            ]

            total_synced = 0

            for table_name in tables_to_sync:
                try:
                    # Read from Snowflake
                    df = self.spark.read \
                        .format("snowflake") \
                        .options(**self.snowflake_config) \
                        .option("dbtable", f"SUPERSUITE_{table_name.upper()}") \
                        .load()

                    if df.count() > 0:
                        # Convert to Neo4j format and write
                        neo4j_label = table_name.title()  # Projects, Files, etc.

                        # Add sync metadata
                        from pyspark.sql.functions import current_timestamp, lit
                        df = df.withColumn("last_synced", current_timestamp())
                        df = df.withColumn("sync_source", lit("snowflake_to_neo4j"))

                        # Write to Neo4j
                        df.write \
                            .format("org.neo4j.spark.DataSource") \
                            .mode("overwrite") \
                            .option("url", self.neo4j_config["url"]) \
                            .option("authentication.basic.username", self.neo4j_config["user"]) \
                            .option("authentication.basic.password", self.neo4j_config["password"]) \
                            .option("labels", f":{neo4j_label}") \
                            .save()

                        count = df.count()
                        total_synced += count
                        logger.info(f"✅ Synced {count} {table_name} from Snowflake to Neo4j")

                except Exception as e:
                    logger.warning(f"⚠️ Failed to sync {table_name}: {e}")
                    continue

            logger.info(f"✅ Completed Snowflake → Neo4j sync: {total_synced} total records")
            return total_synced

        except Exception as e:
            logger.error(f"❌ Failed to sync Snowflake to Neo4j: {e}")
            raise

    def update_sync_metadata(self):
        """Update sync metadata table with current sync information"""
        logger.info("🔄 Updating sync metadata...")

        try:
            # Create sync metadata DataFrame
            from pyspark.sql import Row
            from pyspark.sql.functions import current_timestamp

            sync_metadata = Row(
                sync_id=f"sync_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                sync_timestamp=current_timestamp(),
                neo4j_url=self.neo4j_config["url"],
                snowflake_database=self.snowflake_config["sfDatabase"],
                snowflake_schema=self.snowflake_config["sfSchema"],
                status="COMPLETED"
            )

            metadata_df = self.spark.createDataFrame([sync_metadata])

            # Save to Snowflake
            metadata_df.write \
                .format("snowflake") \
                .options(**self.snowflake_config) \
                .option("dbtable", "SUPERSUITE_SYNC_METADATA") \
                .mode("append") \
                .save()

            logger.info("✅ Sync metadata updated")

        except Exception as e:
            logger.error(f"❌ Failed to update sync metadata: {e}")
            raise

    def run_full_sync(self) -> Dict[str, int]:
        """Run complete synchronization from Neo4j to Snowflake"""
        logger.info("🚀 Starting full Neo4j to Snowflake sync...")

        start_time = datetime.now()

        try:
            # Initialize Spark
            self.initialize_spark()

            # Run sync operations
            results = {
                "entities": self.sync_entities(),
                "relationships": self.sync_relationships(),
                "chunks": self.sync_document_chunks(),
                "projects": self.sync_projects()
            }

            # Update metadata
            self.update_sync_metadata()

            # Calculate duration
            duration = datetime.now() - start_time
            results["duration_seconds"] = duration.total_seconds()

            logger.info("✅ Full sync completed successfully")
            logger.info(f"📊 Sync Summary: {results}")

            return results

        except Exception as e:
            logger.error(f"❌ Full sync failed: {e}")
            raise
        finally:
            if self.spark:
                self.spark.stop()
                logger.info("🔌 Spark session stopped")

def main():
    """Main entry point for the sync job"""
    try:
        # Validate environment
        required_env_vars = [
            "SNOWFLAKE_ACCOUNT", "SNOWFLAKE_USER", "SNOWFLAKE_PASSWORD",
            "NEO4J_URI", "NEO4J_USER", "NEO4J_PASSWORD"
        ]

        missing_vars = [var for var in required_env_vars if not os.getenv(var)]
        if missing_vars:
            logger.error(f"❌ Missing required environment variables: {missing_vars}")
            sys.exit(1)

        # Run sync
        sync = Neo4jSnowflakeSync()
        results = sync.run_full_sync()

        # Print results
        print("\n" + "="*50)
        print("SYNC RESULTS")
        print("="*50)
        for key, value in results.items():
            print(f"{key}: {value}")
        print("="*50)

    except Exception as e:
        logger.error(f"❌ Sync job failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()