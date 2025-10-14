# Hello World Snowflake Notebook

A simple "Hello World" notebook demonstrating Snowflake Notebooks deployment with Python automation.

## 🚀 Quick Deploy

```bash
cd ~/Desktop/lyzr-hackathon/code/notebooks/hello-world
python3 deploy_notebook.py
```

**Access**: https://app.snowflake.com/fhweltt/xs07400/#/notebooks/SNOWFLAKE_LEARNING_DB.PUBLIC.HELLO_WORLD_NOTEBOOK

## 📓 Notebook Contents

1. **Markdown**: "# Hello World Notebook"
2. **Markdown**: Description
3. **Python**: `print("Hello, World!")`
4. **SQL**: Query showing current user and timestamp

## 📂 Files

- `hello_world.ipynb` - Jupyter notebook
- `deploy_notebook.py` - Automated deployment script
- `snowflake.yml` - Snowflake CLI configuration

## 🔐 Prerequisites

1. Create `.env` file in project root with:
   ```bash
   SNOWFLAKE_ACCOUNT=FHWELTT-XS07400
   SNOWFLAKE_USER=HARSHITCODES
   SNOWFLAKE_PASSWORD=your_password
   SNOWFLAKE_ROLE=ACCOUNTADMIN
   SNOWFLAKE_WAREHOUSE=COMPUTE_WH
   SNOWFLAKE_DATABASE=SNOWFLAKE_LEARNING_DB
   SNOWFLAKE_SCHEMA=PUBLIC
   ```

2. Install dependencies:
   ```bash
   pip3 install snowflake-connector-python python-dotenv
   ```

## 📚 Documentation

See `notes/SNOWFLAKE_NOTEBOOK_SETUP.md` for complete documentation.
