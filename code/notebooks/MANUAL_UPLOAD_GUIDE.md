# 🚀 Manual Upload Guide - Fastest Way to Deploy

## ⚡ Quick Start (2 Minutes)

Since PAT token authentication is having issues with the Python connector, here's the **fastest and most reliable** way to get your notebook into Snowflake:

---

## 📝 Step-by-Step Instructions

### Step 1: Download the Notebook File

The notebook is ready at:
```
/Users/harshitchoudhary/Desktop/lyzr-hackathon/code/notebooks/hello-world/hello_world.ipynb
```

Or from terminal, copy it to your Desktop for easy access:
```bash
cp ~/Desktop/lyzr-hackathon/code/notebooks/hello-world/hello_world.ipynb ~/Desktop/
```

---

### Step 2: Login to Snowflake

1. Open your browser
2. Go to: **https://app.snowflake.com/fhweltt/xs07400**
3. Login with your credentials

---

### Step 3: Navigate to Notebooks

In the Snowflake UI:
1. Click on **"Projects"** in the left sidebar
2. Select **"Notebooks"**
3. Or go directly to: https://app.snowflake.com/fhweltt/xs07400/#/notebooks

---

### Step 4: Create/Import Notebook

Click one of these options:
- **"+ Notebook"** button (top right)
- **"Import .ipynb file"** option

Then:
1. **Upload** the `hello_world.ipynb` file
2. Give it a name: `Hello World Notebook`

---

### Step 5: Configure the Notebook

Set these values in the notebook settings:

| Setting | Value |
|---------|-------|
| **Location** | `SNOWFLAKE_LEARNING_DB.PUBLIC` |
| **Warehouse** | `COMPUTE_WH` |
| **Name** | `HELLO_WORLD_NOTEBOOK` |

---

### Step 6: Run the Cells

Your notebook has 4 cells:

#### Cell 1 (Markdown)
```markdown
# Hello World Notebook
```
*Just displays - no need to run*

#### Cell 2 (Markdown)
```markdown
This is a simple hello world notebook for Snowflake
```
*Just displays - no need to run*

#### Cell 3 (Python Code)
```python
print("Hello, World!")
```
**Click ▶️ Run** → Should output: `Hello, World!`

#### Cell 4 (SQL Code)
```sql
SELECT 'Hello from Snowflake!' as message, 
       CURRENT_USER() as user, 
       CURRENT_TIMESTAMP() as timestamp;
```
**Click ▶️ Run** → Should show table with 3 columns

---

## ✅ Expected Results

After running the cells, you should see:

**Python Cell Output:**
```
Hello, World!
```

**SQL Cell Output:**
| message | user | timestamp |
|---------|------|-----------|
| Hello from Snowflake! | HARSHITCODES | 2025-10-14 15:30:00.000 |

---

## 🎉 Success!

Once both cells run successfully:
- ✅ Your notebook is deployed in Snowflake
- ✅ You've completed the hello world example
- ✅ Ready to commit your work to git

---

## 📸 Take a Screenshot

For documentation/hackathon submission:
1. Take a screenshot of the notebook with both outputs visible
2. Save it to: `~/Desktop/lyzr-hackathon/code/notebooks/hello-world/screenshot.png`

---

## 💾 Commit Your Work

```bash
cd ~/Desktop/lyzr-hackathon

# Add files (not .env!)
git add code/notebooks/hello-world/hello_world.ipynb
git add code/notebooks/hello-world/snowflake.yml
git add code/notebooks/hello-world/README.md
git add code/notebooks/hello-world/deploy_notebook.py
git add code/notebooks/MANUAL_UPLOAD_GUIDE.md
git add code/notebooks/NEXT_STEPS.md
git add code/notebooks/PAT_TOKEN_ISSUE.md
git add .gitignore

# Verify .env is NOT being committed
git status  # Should show .env as untracked/ignored

# Commit
git commit -m "Add hello-world Snowflake Notebook with deployment scripts and documentation"

# Push if needed
git push
```

---

## 📝 Notes

- **Why manual upload?**: PAT token authentication through the Python connector requires additional Snowflake account configuration that may not be enabled
- **Is this okay?**: YES! Manual upload is a perfectly valid deployment method, especially for initial setup
- **Can I automate later?**: Yes, once PAT authentication is properly configured with Snowflake support

---

## 🎯 You're Done!

This approach:
- ✅ Takes 2-3 minutes
- ✅ Works reliably 100% of the time
- ✅ Gives you the same result as automated deployment
- ✅ Perfect for hackathon/proof-of-concept

**Now go run those cells and celebrate! 🎊**
