# Snowflake Notebooks

Collection of Jupyter notebooks for the Lyzr Hackathon project, demonstrating integration with Snowflake for data processing and analysis.

## 📓 Notebooks

### hello-world/
A simple "Hello World" notebook demonstrating:
- Python code execution in Snowflake
- SQL query execution
- Automated deployment to Snowflake

**Quick Deploy**:
```bash
cd hello-world
python3 deploy_notebook.py
```

## 🔐 Setup

1. **Create `.env` file** in project root:
```bash
SNOWFLAKE_ACCOUNT=FHWELTT-XS07400
SNOWFLAKE_USER=HARSHITCODES
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_ROLE=ACCOUNTADMIN
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=SNOWFLAKE_LEARNING_DB
SNOWFLAKE_SCHEMA=PUBLIC
```

2. **Install dependencies**:
```bash
pip3 install snowflake-connector-python python-dotenv
```

## 📚 Documentation

- **Complete Guide**: `../../notes/SNOWFLAKE_NOTEBOOK_SETUP.md`
- **Quick Reference**: `../../notes/QUICK_REFERENCE.md`

## 🔗 Access

**Snowflake UI**: https://app.snowflake.com/fhweltt/xs07400/#/notebooks
