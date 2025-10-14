# Snowflake Notebook - Quick Reference Card

## 🚀 Quick Deploy (30 seconds)

```bash
cd ~/Desktop/lyzr-hackathon/code/notebooks/hello-world
python3 deploy_notebook.py
```

**Access**: https://app.snowflake.com/fhweltt/xs07400/#/notebooks/SNOWFLAKE_LEARNING_DB.PUBLIC.HELLO_WORLD_NOTEBOOK

---

## 🔐 Credentials (from .env)

```
Account:   FHWELTT-XS07400
User:      HARSHITCODES
Password:  ***REMOVED***
Role:      ACCOUNTADMIN
Warehouse: COMPUTE_WH
Database:  SNOWFLAKE_LEARNING_DB
Schema:    PUBLIC
```

---

## 📂 Key Files

| File | Location | Purpose |
|------|----------|---------|
| Notebook | `code/notebooks/hello-world/hello_world.ipynb` | Jupyter notebook |
| Deploy Script | `code/notebooks/hello-world/deploy_notebook.py` | Automated deployment |
| Credentials | `.env` | Snowflake credentials (NEVER commit) |
| Config | `snowflake.yml` | Snowflake CLI config |

---

## 📓 Notebook Cells

1. **Markdown**: "# Hello World Notebook"
2. **Markdown**: Description
3. **Python**: `print("Hello, World!")`
4. **SQL**: `SELECT 'Hello from Snowflake!' as message, CURRENT_USER() as user, CURRENT_TIMESTAMP() as timestamp;`

---

## 🔧 Common Commands

```bash
# Deploy notebook
python3 deploy_notebook.py

# Verify .env is gitignored
git check-ignore .env

# Check git status
git status

# Commit (without secrets)
git add code/notebooks/ notes/ .gitignore
git commit -m "Add Snowflake notebook deployment"
```

---

## ⚠️ Security Checklist

- ✅ `.env` in `.gitignore`
- ✅ `.env` permissions = 600
- ✅ Never commit passwords/tokens
- ✅ Always verify with `git status` before commit

---

## 🐛 Quick Troubleshooting

| Issue | Solution |
|-------|----------|
| Authentication failed | Check password in `.env` |
| Module not found | `pip3 install snowflake-connector-python python-dotenv` |
| File not found | Ensure you're in correct directory |
| .env committed | `git reset HEAD .env` then add to `.gitignore` |

---

## 📞 Support

**Full Documentation**: `/Users/harshitchoudhary/Desktop/lyzr-hackathon/notes/SNOWFLAKE_NOTEBOOK_SETUP.md`

**Snowflake Docs**: https://docs.snowflake.com/en/user-guide/ui-snowsight/notebooks
