# Hello World Snowflake Notebook

A simple "Hello World" notebook demonstrating Snowflake Notebooks deployment using the Snowflake CLI.

## 📁 Project Structure

```
hello-world/
├── hello_world.ipynb    # Jupyter notebook with Python and SQL cells
├── snowflake.yml        # Snowflake CLI project configuration
└── README.md           # This file
```

## 📓 Notebook Contents

The notebook includes:
1. **Markdown Cell**: Title header
2. **Markdown Cell**: Description
3. **Python Cell**: Prints "Hello, World!"
4. **SQL Cell**: Executes a simple Snowflake query showing current user and timestamp

## 🚀 Deployment

### Prerequisites

1. **Snowflake CLI installed**
   ```bash
   # Check if installed
   snow --version
   ```

2. **Snowflake connection configured** in `~/.snowflake/config.toml`
   ```toml
   [connections.default]
   account = "FHWELTT-XS07400"
   user = "HARSHITCODES"
   authenticator = "oauth"
   token = "<your_pat_token>"
   role = "ACCOUNTADMIN"
   warehouse = "COMPUTE_WH"
   database = "SNOWFLAKE_LEARNING_DB"
   schema = "PUBLIC"
   ```

### Deploy to Snowflake

```bash
# Navigate to project directory
cd /Users/harshitchoudhary/Desktop/lyzr-hackathon/code/notebooks/hello-world

# Deploy the notebook
snow notebook deploy

# Get the notebook URL
snow notebook get-url --name hello_world

# Or open directly in browser
snow notebook open --name hello_world
```

## 🔗 Access

After deployment, access your notebook at:
- **Direct URL**: https://app.snowflake.com/fhweltt/xs07400/#/notebooks
- **Via CLI**: `snow notebook open --name hello_world`

## 📝 Notes

- The notebook is deployed to: `SNOWFLAKE_LEARNING_DB.PUBLIC`
- Files are staged in: `@SNOWFLAKE_LEARNING_DB.PUBLIC.NOTEBOOKS_STAGE`
- Compute warehouse: `COMPUTE_WH`

## 🔒 Security

- Never commit `.env` files containing PAT tokens
- Snowflake credentials are stored locally in `~/.snowflake/config.toml` (not in repo)
- PAT token stored in project root `.env` (gitignored)

## 📚 References

- [Snowflake CLI Documentation](https://docs.snowflake.com/en/developer-guide/snowflake-cli)
- [Snowflake Notebooks Documentation](https://docs.snowflake.com/en/user-guide/ui-snowsight/notebooks)
- [OAuth Personal Access Tokens](https://docs.snowflake.com/en/user-guide/oauth-personal-access-token)
