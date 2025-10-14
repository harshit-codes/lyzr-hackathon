# 🚀 Next Steps: Deploy Hello World Notebook to Snowflake

## ✅ What's Already Done

I've set up the following for you:

1. **✅ Secured your PAT token**
   - Created `.env` file with your Snowflake PAT
   - Added `.env` to `.gitignore` (never committed to git)
   - Set proper file permissions (chmod 600)

2. **✅ Created the notebook**
   - Location: `code/notebooks/hello-world/hello_world.ipynb`
   - Contains 4 cells:
     - Markdown: "# Hello World Notebook"
     - Markdown: Description
     - Python: `print("Hello, World!")`
     - SQL: Query showing current user and timestamp

3. **✅ Created Snowflake project configuration**
   - File: `code/notebooks/hello-world/snowflake.yml`
   - Defines stage and notebook deployment settings

4. **✅ Configured Snowflake CLI connection**
   - File: `~/.snowflake/config.toml`
   - Uses `externalbrowser` authentication (opens browser for login)

5. **✅ Created documentation**
   - README in the hello-world directory
   - This NEXT_STEPS guide

---

## 🔧 What You Need to Do Now

### Step 1: Test Snowflake Connection

Open a **new terminal** and run:

```bash
cd ~/Desktop/lyzr-hackathon
snow connection test
```

**Expected behavior**: 
- Your browser will open
- Log into Snowflake
- Connection test should succeed

**If it fails**:
- Verify you're logged into Snowflake in your browser
- Check that your account URL is correct: `FHWELTT-XS07400`
- Ensure ACCOUNTADMIN role and COMPUTE_WH warehouse exist

---

### Step 2: Create the Stage (if needed)

Run this to create the stage where notebook files will be uploaded:

```bash
snow sql -q "CREATE STAGE IF NOT EXISTS SNOWFLAKE_LEARNING_DB.PUBLIC.NOTEBOOKS_STAGE"
```

---

### Step 3: Deploy the Notebook

Navigate to the project directory and deploy:

```bash
cd ~/Desktop/lyzr-hackathon/code/notebooks/hello-world
snow notebook deploy
```

**What this does**:
- Uploads `hello_world.ipynb` to the Snowflake stage
- Creates a Snowflake Notebook object in your account
- Links it to COMPUTE_WH warehouse

---

### Step 4: Open Your Notebook

After successful deployment, get the URL:

```bash
snow notebook get-url hello_world
```

Or open it directly:

```bash
snow notebook open hello_world
```

Or navigate manually:
- Go to: https://app.snowflake.com/fhweltt/xs07400/#/notebooks
- Find "HELLO_WORLD" in the list
- Click to open and run cells

---

### Step 5: Verify It Works

In the Snowflake Notebook UI:

1. **Run the Python cell** → Should print: `Hello, World!`
2. **Run the SQL cell** → Should show:
   - message: "Hello from Snowflake!"
   - user: "HARSHITCODES"  
   - timestamp: Current time

---

### Step 6: Commit Your Work

Only commit non-secret files:

```bash
cd ~/Desktop/lyzr-hackathon

# Stage the files
git add code/notebooks/hello-world/hello_world.ipynb
git add code/notebooks/hello-world/snowflake.yml
git add code/notebooks/hello-world/README.md
git add code/notebooks/NEXT_STEPS.md
git add .gitignore

# Commit
git commit -m "Add hello-world Snowflake Notebook with deployment config"

# Check what's NOT committed (should include .env)
git status
```

**NEVER commit**:
- `.env` (contains your PAT)
- `~/.snowflake/config.toml` (local config)

---

## 🐛 Troubleshooting

### Issue: "Invalid OAuth access token"

**Solution**: We're now using `externalbrowser` auth instead of OAuth token. This will open your browser for authentication.

### Issue: "Stage does not exist"

**Solution**: Run Step 2 above to create the stage manually.

### Issue: "snow: command not found"

**Solution**: Snowflake CLI is installed via pip. Run:
```bash
snow --version
```
If it fails, the CLI might not be in your PATH. Try:
```bash
python3 -m snowflake.cli --version
```

### Issue: Connection test hangs

**Solution**: 
1. Close any open Snowflake browser tabs
2. Try the connection test again
3. A browser window should open for authentication

### Issue: Notebook deploy fails with "entity not found"

**Solution**: Check the snowflake.yml file uses correct syntax for your CLI version:
```bash
cd code/notebooks/hello-world
snow project validate
```

---

## 📚 Useful Commands

```bash
# List connections
snow connection list

# Test connection
snow connection test

# Execute SQL query
snow sql -q "SELECT CURRENT_USER()"

# List notebooks
snow object list notebook

# Get notebook URL
snow notebook get-url hello_world

# Execute notebook
snow notebook execute hello_world

# View Snowflake CLI help
snow --help
snow notebook --help
```

---

## 📖 Documentation References

- **Snowflake CLI**: https://docs.snowflake.com/en/developer-guide/snowflake-cli
- **Notebooks**: https://docs.snowflake.com/en/user-guide/ui-snowsight/notebooks
- **OAuth/PAT**: https://docs.snowflake.com/en/user-guide/oauth-personal-access-token
- **Project Definition**: https://docs.snowflake.com/en/developer-guide/snowflake-cli/project-definition

---

## ✨ Summary

You're all set! Just run:

1. `snow connection test` (authenticate in browser)
2. `snow sql -q "CREATE STAGE IF NOT EXISTS SNOWFLAKE_LEARNING_DB.PUBLIC.NOTEBOOKS_STAGE"`
3. `cd code/notebooks/hello-world && snow notebook deploy`
4. `snow notebook open hello_world`

That's it! Your Hello World notebook will be live in Snowflake. 🎉
