# Remote Production Testing Report
**Generated:** 2025-10-16 01:40:34

## Test Summary
- **Total Tests:** 8
- **Passed:** 2
- **Failed:** 6
- **Success Rate:** 25.0%
- **Duration:** 6.0 seconds

## Detailed Results
### ✅ Neo4J Connection
**Status:** PASSED
**Message:** Successfully connected to Neo4j: Neo4j connection successful
**Details:**
```json
{
  "uri": "neo4j+s://b70333ab.databases.neo4j.io"
}
```

### ✅ Snowflake Connection
**Status:** PASSED
**Message:** Successfully connected to Snowflake: ('DA87984', 'HARSHITCODES', 'LYZRHACK', 'PUBLIC')
**Details:**
```json
{
  "account": "DA87984",
  "user": "HARSHITCODES",
  "database": "LYZRHACK",
  "schema": "PUBLIC"
}
```

### ❌ Graph Api Service
**Status:** FAILED
**Message:** Graph API service test failed: HTTPConnectionPool(host='localhost', port=8000): Max retries exceeded with url: /health (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x11e96f920>: Failed to establish a new connection: [Errno 61] Connection refused'))
**Details:**
```json
{
  "error": "HTTPConnectionPool(host='localhost', port=8000): Max retries exceeded with url: /health (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x11e96f920>: Failed to establish a new connection: [Errno 61] Connection refused'))"
}
```

### ❌ Dynamic Schema Creation
**Status:** FAILED
**Message:** Dynamic schema creation test failed: 100038 (22018): 01bfbbba-3202-03db-0010-ab2a0002b962: DML operation to table SUPERSUITE_PERSON_TEST failed on column AGE with error: Numeric value 'Test Value' is not recognized
**Details:**
```json
{
  "error": "100038 (22018): 01bfbbba-3202-03db-0010-ab2a0002b962: DML operation to table SUPERSUITE_PERSON_TEST failed on column AGE with error: Numeric value 'Test Value' is not recognized"
}
```

### ❌ Bidirectional Sync
**Status:** FAILED
**Message:** Bidirectional sync test failed: No module named 'pyspark'
**Details:**
```json
{
  "error": "No module named 'pyspark'"
}
```

### ❌ Cypher Query Integration
**Status:** FAILED
**Message:** Cypher query integration test failed: HTTPConnectionPool(host='localhost', port=8000): Max retries exceeded with url: /cypher (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x11e836ab0>: Failed to establish a new connection: [Errno 61] Connection refused'))
**Details:**
```json
{
  "error": "HTTPConnectionPool(host='localhost', port=8000): Max retries exceeded with url: /cypher (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x11e836ab0>: Failed to establish a new connection: [Errno 61] Connection refused'))"
}
```

### ❌ Supersuite End To End
**Status:** FAILED
**Message:** SuperSuite end-to-end test failed: HTTPConnectionPool(host='localhost', port=8000): Max retries exceeded with url: /sync (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x11e836300>: Failed to establish a new connection: [Errno 61] Connection refused'))
**Details:**
```json
{
  "error": "HTTPConnectionPool(host='localhost', port=8000): Max retries exceeded with url: /sync (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x11e836300>: Failed to establish a new connection: [Errno 61] Connection refused'))"
}
```
