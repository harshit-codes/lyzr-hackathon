-- SuperSuite Graph Data Tables for Snowflake
-- These tables store synced data from Neo4j via Spark jobs

-- Create database and schema if they don't exist
CREATE DATABASE IF NOT EXISTS SUPERSUITE;
USE DATABASE SUPERSUITE;
CREATE SCHEMA IF NOT EXISTS PUBLIC;

-- Table to store entity nodes from Neo4j
CREATE OR REPLACE TABLE SUPERSUITE_ENTITIES (
    -- Neo4j internal ID
    neo4j_id STRING,

    -- Entity properties
    entity_id STRING,
    name STRING,
    type STRING,
    labels ARRAY,
    properties VARIANT,

    -- Sync metadata
    last_synced TIMESTAMP_NTZ,
    sync_source STRING,

    -- Primary key
    PRIMARY KEY (neo4j_id)
);

-- Table to store relationships from Neo4j
CREATE OR REPLACE TABLE SUPERSUITE_RELATIONSHIPS (
    -- Neo4j internal IDs
    source_neo4j_id STRING,
    target_neo4j_id STRING,
    relationship_id STRING,

    -- Relationship properties
    relationship_type STRING,
    properties VARIANT,

    -- Source and target entity info
    source_entity_id STRING,
    source_entity_name STRING,
    source_entity_type STRING,
    target_entity_id STRING,
    target_entity_name STRING,
    target_entity_type STRING,

    -- Sync metadata
    last_synced TIMESTAMP_NTZ,
    sync_source STRING,

    -- Primary key
    PRIMARY KEY (relationship_id),

    -- Foreign keys
    FOREIGN KEY (source_neo4j_id) REFERENCES SUPERSUITE_ENTITIES(neo4j_id),
    FOREIGN KEY (target_neo4j_id) REFERENCES SUPERSUITE_ENTITIES(neo4j_id)
);

-- Table to store document chunks from Neo4j
CREATE OR REPLACE TABLE SUPERSUITE_CHUNKS (
    -- Neo4j internal ID
    neo4j_id STRING,

    -- Chunk properties
    chunk_id STRING,
    content STRING,
    embedding ARRAY,  -- Vector embedding if available
    metadata VARIANT,

    -- Document relationship
    document_id STRING,
    document_name STRING,
    project_id STRING,

    -- Chunk metadata
    chunk_index INTEGER,
    total_chunks INTEGER,
    chunk_size INTEGER,

    -- Sync metadata
    last_synced TIMESTAMP_NTZ,
    sync_source STRING,

    -- Primary key
    PRIMARY KEY (neo4j_id)
);

-- Table to store project metadata from Neo4j
CREATE OR REPLACE TABLE SUPERSUITE_PROJECTS (
    -- Neo4j internal ID
    neo4j_id STRING,

    -- Project properties
    project_id STRING,
    project_name STRING,
    description STRING,
    created_date TIMESTAMP_NTZ,
    metadata VARIANT,

    -- Sync metadata
    last_synced TIMESTAMP_NTZ,
    sync_source STRING,

    -- Primary key
    PRIMARY KEY (neo4j_id)
);

-- Table to track sync job metadata
CREATE OR REPLACE TABLE SUPERSUITE_SYNC_METADATA (
    -- Sync job identifier
    sync_id STRING,

    -- Sync timing
    sync_timestamp TIMESTAMP_NTZ,

    -- Connection info
    neo4j_url STRING,
    snowflake_database STRING,
    snowflake_schema STRING,

    -- Sync status
    status STRING,  -- 'COMPLETED', 'FAILED', 'RUNNING'

    -- Primary key
    PRIMARY KEY (sync_id, sync_timestamp)
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_entities_type ON SUPERSUITE_ENTITIES(type);
CREATE INDEX IF NOT EXISTS idx_entities_name ON SUPERSUITE_ENTITIES(name);
CREATE INDEX IF NOT EXISTS idx_entities_last_synced ON SUPERSUITE_ENTITIES(last_synced);

CREATE INDEX IF NOT EXISTS idx_relationships_type ON SUPERSUITE_RELATIONSHIPS(relationship_type);
CREATE INDEX IF NOT EXISTS idx_relationships_source ON SUPERSUITE_RELATIONSHIPS(source_entity_id);
CREATE INDEX IF NOT EXISTS idx_relationships_target ON SUPERSUITE_RELATIONSHIPS(target_entity_id);
CREATE INDEX IF NOT EXISTS idx_relationships_last_synced ON SUPERSUITE_RELATIONSHIPS(last_synced);

CREATE INDEX IF NOT EXISTS idx_chunks_document ON SUPERSUITE_CHUNKS(document_id);
CREATE INDEX IF NOT EXISTS idx_chunks_project ON SUPERSUITE_CHUNKS(project_id);
CREATE INDEX IF NOT EXISTS idx_chunks_last_synced ON SUPERSUITE_CHUNKS(last_synced);

CREATE INDEX IF NOT EXISTS idx_projects_name ON SUPERSUITE_PROJECTS(project_name);
CREATE INDEX IF NOT EXISTS idx_projects_last_synced ON SUPERSUITE_PROJECTS(last_synced);

CREATE INDEX IF NOT EXISTS idx_sync_metadata_timestamp ON SUPERSUITE_SYNC_METADATA(sync_timestamp);
CREATE INDEX IF NOT EXISTS idx_sync_metadata_status ON SUPERSUITE_SYNC_METADATA(status);

-- Grant permissions (adjust as needed for your Snowflake setup)
-- GRANT USAGE ON DATABASE SUPERSUITE TO ROLE SUPERSUITE_ROLE;
-- GRANT USAGE ON SCHEMA SUPERSUITE.PUBLIC TO ROLE SUPERSUITE_ROLE;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA SUPERSUITE.PUBLIC TO ROLE SUPERSUITE_ROLE;

-- Comments for documentation
COMMENT ON TABLE SUPERSUITE_ENTITIES IS 'Entity nodes synced from Neo4j graph database';
COMMENT ON TABLE SUPERSUITE_RELATIONSHIPS IS 'Relationships between entities synced from Neo4j';
COMMENT ON TABLE SUPERSUITE_CHUNKS IS 'Document chunks with embeddings synced from Neo4j';
COMMENT ON TABLE SUPERSUITE_PROJECTS IS 'Project metadata synced from Neo4j';
COMMENT ON TABLE SUPERSUITE_SYNC_METADATA IS 'Metadata about sync job executions';