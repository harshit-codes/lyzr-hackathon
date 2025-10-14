# ⚠️ PAT Token Authentication Issue

## 🚨 Current Problem

Your PAT (Personal Access Token) is returning "Invalid OAuth access token" error. This means the token is either:

1. **Expired** 
2. **Invalid format**
3. **Not properly configured in Snowflake**

---

## 🔧 Solution Options

### Option A: Generate a New PAT Token (Recommended)

**Step 1: Login to Snowflake**
- Go to: https://app.snowflake.com/fhweltt/xs07400
- Login with your credentials

**Step 2: Navigate to Personal Access Tokens**
- Click your name in the bottom-left corner
- Select "My Profile"
- Go to "Personal Access Tokens" tab

**Step 3: Create New Token**
- Click "**+ Generate Token**" or "**+ Token**"
- Name: `CLI Access` or `Hackathon Token`
- Expiration: 90 days (or as needed)
- Click **Generate**
- **⚠️ COPY THE TOKEN IMMEDIATELY** (it won't be shown again!)

**Step 4: Update .env File**
```bash
cd ~/Desktop/lyzr-hackathon
nano .env  # or use VS Code: code .env
```

Replace the `SNOWFLAKE_TOKEN=...` line with your new token:
```
SNOWFLAKE_TOKEN=your_new_token_here
```

**Step 5: Test Again**
```bash
cd code/notebooks/hello-world
python3 deploy_notebook.py
```

---

### Option B: Manual Upload to Snowflake UI

If PAT tokens continue to fail, you can upload manually:

**Step 1: Go to Snowflake Notebooks**
- Navigate to: https://app.snowflake.com/fhweltt/xs07400/#/notebooks

**Step 2: Create New Notebook**
- Click "**+ Notebook**" or "**Import**"
- Choose "**Import from file**"
- Upload `hello_world.ipynb`

**Step 3: Configure Notebook**
- Set **Warehouse**: `COMPUTE_WH`
- Set **Database**: `SNOWFLAKE_LEARNING_DB`
- Set **Schema**: `PUBLIC`

**Step 4: Run the Cells**
- Python cell: `print("Hello, World!")`
- SQL cell: `SELECT 'Hello from Snowflake!' as message, CURRENT_USER() as user, CURRENT_TIMESTAMP() as timestamp;`

---

### Option C: Alternative Python Script (Password Auth)

If you prefer to use username/password instead of PAT:

**Step 1: Add password to .env**
```bash
echo "SNOWFLAKE_PASSWORD=your_password_here" >> ~/Desktop/lyzr-hackathon/.env
```

**Step 2: Create alternative deployment script**
```python
# This would use password instead of token
conn = snowflake.connector.connect(
    account=SNOWFLAKE_ACCOUNT,
    user=SNOWFLAKE_USER,
    password=os.getenv('SNOWFLAKE_PASSWORD'),  # Instead of token
    role=SNOWFLAKE_ROLE,
    warehouse=SNOWFLAKE_WAREHOUSE,
    database=SNOWFLAKE_DATABASE,
    schema=SNOWFLAKE_SCHEMA
)
```

---

## 📝 Next Steps

1. **Try Option A first** (new PAT token) - this is the most secure
2. If that fails, **use Option B** (manual upload) - this definitely works
3. Option C is there if you need programmatic access with password

## 🎯 Your Goal

Get the hello world notebook running in Snowflake with these 4 cells:
1. Markdown: "# Hello World Notebook"
2. Markdown: Description  
3. Python: `print("Hello, World!")`
4. SQL: Query showing current user and timestamp

**The notebook is already created and ready to upload!**

---

## 📞 Need Help?

If you continue having issues:
1. Check the Snowflake documentation for PAT tokens
2. Contact Snowflake support about PAT authentication
3. Use the manual upload method (Option B) as a reliable fallback

The notebook files are ready - it's just an authentication issue preventing automatic deployment.