# 🚨 IMMEDIATE ACTIONS - DO THIS NOW!

## ⏱️ Time Estimate: 30 minutes

### Step 1: Rotate Credentials (10 minutes)

#### Snowflake Password
```bash
# Open Snowflake
open https://app.snowflake.com/

# Change password in UI:
# Profile → Account → Change Password
# Use a strong password (20+ characters, random)
```

#### DeepSeek API Key  
```bash
# Open DeepSeek
open https://platform.deepseek.com/api_keys

# 1. Revoke: ***REDACTED_DEEPSEEK_API_KEY***
# 2. Generate new key
# 3. Copy new key
```

#### Update .env File
```bash
cd /Users/harshitchoudhary/Desktop/lyzr-hackathon

# Edit .env with new credentials
nano .env

# Update these lines:
# SNOWFLAKE_PASSWORD=<paste-new-password>
# DEEPSEEK_API_KEY=<paste-new-key>

# Save and exit (Ctrl+X, Y, Enter)
```

---

### Step 2: Remove Secrets from Files (5 minutes)

```bash
cd /Users/harshitchoudhary/Desktop/lyzr-hackathon

# Fix superscan_snowflake_demo.py
sed -i '' 's/DEEPSEEK_API_KEY = "***REDACTED_DEEPSEEK_API_KEY***"/DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")/' code/notebooks/superscan_snowflake_demo.py

# Fix test_superscan_flow.py  
sed -i '' "s/DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', '***REDACTED_DEEPSEEK_API_KEY***')/DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')/" code/notebooks/test_superscan_flow.py

# Commit the fixes
git add code/notebooks/superscan_snowflake_demo.py code/notebooks/test_superscan_flow.py
git commit -m "security: Remove hardcoded API keys, use environment variables"
```

---

### Step 3: Clean Git History (10 minutes)

```bash
cd /Users/harshitchoudhary/Desktop/lyzr-hackathon

# Run the cleanup script
./cleanup_secrets.sh

# Type "yes" when prompted
```

---

### Step 4: Force Push to GitHub (2 minutes)

```bash
cd /Users/harshitchoudhary/Desktop/lyzr-hackathon

# Force push to overwrite history
git push origin main --force
git push origin --force --all
git push origin --force --tags
```

---

### Step 5: Verify (3 minutes)

```bash
cd /Users/harshitchoudhary/Desktop/lyzr-hackathon

# Should return NOTHING:
grep -r "***REDACTED_DEEPSEEK_API_KEY***" . --exclude-dir=notes/inspiration --exclude-dir=.git
grep -r "***REDACTED_PASSWORD***" . --exclude-dir=notes/inspiration --exclude-dir=.git

# Check Git history (should also return NOTHING):
git log --all -S "***REDACTED_DEEPSEEK_API_KEY***" --oneline
git log --all -S "***REDACTED_PASSWORD***" --oneline
```

---

## ✅ Done!

Once completed, check off these items:

- [ ] Snowflake password changed
- [ ] DeepSeek API key regenerated
- [ ] .env file updated
- [ ] Hardcoded secrets removed from files
- [ ] Git history cleaned
- [ ] Force pushed to GitHub
- [ ] Verified no secrets remain

---

## 📞 Need Help?

If stuck, refer to: `SECURITY_INCIDENT_RESPONSE.md`

---

**IMPORTANT**: Once you've rotated the credentials, the old ones are worthless but still need to be removed from Git history to prevent GitGuardian alerts.
