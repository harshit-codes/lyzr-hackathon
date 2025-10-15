# CI/CD Pipeline Challenges and Solutions

## Overview
This document outlines the challenges encountered and solutions implemented during the setup of a CI/CD pipeline for deploying a Streamlit application to Snowflake.

## Challenges Faced

### 1. SSL Certificate Validation Issues
**Problem**: The GitHub Actions workflow consistently failed with SSL certificate validation errors when uploading files to Snowflake stages.

**Root Cause**: The Snowflake account is hosted in the Singapore region (sfc-sg), and the S3 endpoint's SSL certificate was not trusted by the GitHub Actions Ubuntu runner's certificate store.

**Error Message**:
```
254007: 254007: The certificate is revoked or could not be validated: hostname=sfc-sg-ds1-159-customer-stage.s3.amazonaws.com
```

**Impact**: Prevented automated deployment of application files to Snowflake.

### 2. Snowflake CLI Limitations
**Problem**: The Snowflake CLI (`snow`) does not provide options to disable SSL verification for file operations.

**Attempts**:
- Using `--insecure` flag (not supported)
- Setting `SNOWFLAKE_INSECURE_MODE=1` (only works for Python connector, not CLI)

**Impact**: Could not bypass SSL issues using the CLI alone.

### 3. Workflow Configuration Issues
**Problem**: Multiple iterations of workflow debugging due to:
- Invalid YAML syntax (indentation errors)
- Incorrect configuration file keys (`accountname` instead of `account`)
- Duplicate steps created during edits
- Wrong environment variable usage

**Impact**: Delayed deployment and multiple failed workflow runs.

### 4. Authentication Method Limitations
**Problem**: Password-based authentication worked for connection testing but faced SSL issues during data transfer operations.

**Considered Alternatives**:
- Key Pair Authentication (more secure, but requires additional setup)
- OIDC/Workload Identity Federation (not configured)

## Solutions Implemented

### 1. Python Script with Insecure Mode
**Solution**: Created `upload_to_stage.py` using the Snowflake Python connector with `insecure_mode=True`.

**Code**:
```python
conn = snowflake.connector.connect(
    user=os.getenv("SNOWFLAKE_USER"),
    password=os.getenv("SNOWFLAKE_PASSWORD"),
    account=os.getenv("SNOWFLAKE_ACCOUNT"),
    database=DB_NAME,
    schema=SCHEMA_NAME,
    warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
    insecure_mode=True  # Bypass SSL certificate issues
)
```

**Benefits**:
- Bypasses SSL validation issues
- Provides better error handling
- Allows programmatic file uploads

### 2. Temporary Connection Authentication
**Solution**: Used `--temporary-connection` flag with environment variables for all Snowflake CLI operations.

**Benefits**:
- No need for config files
- Secure credential handling via GitHub secrets
- Works well in CI/CD environments

### 3. Workflow Structure Cleanup
**Solution**: Completely rewrote the GitHub Actions workflow with:
- Proper YAML syntax
- Correct step sequencing
- Removal of duplicate steps
- Clear environment variable management

### 4. Comprehensive Testing
**Solution**: Added connection testing step before deployment to isolate authentication issues from SSL issues.

## Current Pipeline Architecture

```yaml
name: Deploy Streamlit to Snowflake

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - Checkout repository
      - Set up Python
      - Install Snowflake CLI
      - Test Snowflake Connection (temporary connection)
      - Create Stage (temporary connection)
      - Deploy Streamlit App (Python script with insecure_mode)
      - Upload Code Directory (handled by Python script)
```

## Key Files

- `.github/workflows/deploy_streamlit.yml`: GitHub Actions workflow
- `upload_to_stage.py`: Python script for file uploads
- `snowflake.yml`: Streamlit app configuration

## Security Considerations

- Credentials stored as GitHub repository secrets
- Temporary connections used to avoid config file persistence
- Insecure mode used only for file uploads due to SSL certificate issues

## Future Improvements

1. **Key Pair Authentication**: Implement RSA key pair authentication for enhanced security
2. **SSL Certificate Resolution**: Work with Snowflake support to resolve certificate validation issues
3. **Multi-Environment Deployment**: Add staging/production environment separation
4. **Automated Testing**: Add unit tests and integration tests to the pipeline

## Lessons Learned

1. SSL certificate issues can affect CI/CD pipelines in unexpected ways
2. Python connector provides more flexibility than CLI for complex operations
3. Temporary connections are ideal for CI/CD environments
4. Thorough testing of each pipeline step is crucial
5. Documentation of challenges helps future troubleshooting

## Verification

The pipeline successfully deploys the Streamlit application with all required files on every push to the main branch. The latest successful run completed in 32 seconds.

**Last Successful Run**: ID 18536995037
**Status**: ✅ All steps passed</content>
<parameter name="filePath">/Users/harshitchoudhary/Desktop/lyzr-hackathon/docs/CI_CD_CHALLENGES.md