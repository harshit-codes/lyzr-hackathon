# Snowflake Notebook Testing Guide

## 🎯 Quick Start

### 1. Upload Notebook to Snowflake
1. Open your Snowflake console
2. Go to **Projects** → **Notebooks**
3. Click **+ Notebook** → **Import .ipynb**
4. Upload: `code/notebooks/snowflake_superscan_test.ipynb`

### 2. Set Up Environment
Snowflake notebooks use environment variables. Set these in the notebook settings:

```
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_DATABASE=your_database
SNOWFLAKE_SCHEMA=PUBLIC
SNOWFLAKE_WAREHOUSE=your_warehouse
OPENAI_API_KEY=sk-...
DEEPSEEK_API_KEY=sk-...
```

### 3. Run the Notebook
Click **Run All** or execute cells one by one.

---

## 📊 What Gets Tested

✅ Snowflake connection  
✅ Database table creation  
✅ VariantType serialization  
✅ Project creation (with config dict)  
✅ Schema creation (with attributes list)  
✅ Node creation (with structured/unstructured data)  
✅ Data retrieval and verification  
✅ VARIANT column handling  

---

## ✅ Expected Results

Each cell should show:
- ✅ Green checkmarks for successful operations
- No ❌ error messages
- Data correctly stored and retrieved
- Config/metadata as Python dicts (not strings)

---

## 🔧 Alternative: Local Testing

If Snowflake Notebooks aren't available, run locally:

```bash
cd code/notebooks
jupyter notebook snowflake_superscan_test.ipynb
```

Or use the Python test file:
```bash
cd code
python notebooks/test_superscan_flow.py
```

---

## 📝 Test Results

After running, document:
- [ ] All cells executed successfully
- [ ] Project created with ID: ___________
- [ ] Schema created with ID: ___________
- [ ] Node created with ID: ___________
- [ ] VARIANT columns handled correctly
- [ ] Query retrieved data successfully

---

## 🚀 Next Steps After Testing

1. ✅ Review test results
2. ✅ Check Snowflake database tables
3. ✅ Verify data integrity
4. ✅ Run performance benchmarks
5. ✅ Test full document processing pipeline

---

**Guide Created:** October 15, 2025  
**Status:** Ready for Snowflake testing
