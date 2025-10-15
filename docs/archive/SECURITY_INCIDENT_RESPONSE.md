# Security Incident Response: Exposed Credentials

## 🚨 CRITICAL: Immediate Actions Required

GitGuardian has detected **Snowflake Connector Credentials** exposed in your GitHub repository. This is a **HIGH SEVERITY** security incident.

---

## Timeline

- **Detected**: October 14, 2025
- **Repository**: harshit-codes/lyzr-hackathon
- **Exposure**: Public GitHub repository
- **Credentials Type**: Snowflake password, DeepSeek API key

---

## Exposed Credentials

The following credentials were found in Git history:

1. **Snowflake Password**: `***REDACTED_PASSWORD***`
   - Location: Multiple files (`.env` references, notebooks, deployment scripts)
   - Impact: Full access to Snowflake account

2. **DeepSeek API Key**: `***REDACTED_DEEPSEEK_API_KEY***`
   - Location: `superscan_snowflake_demo.py`, `test_superscan_flow.py`
   - Impact: Unauthorized API usage, potential billing charges

---

## Immediate Response Plan (DO THIS NOW!)

### Phase 1: Rotate Credentials (Within 1 hour)

#### 1.1 Rotate Snowflake Password

```bash
# Login to Snowflake
# Method 1: Via Snowsight UI
1. Go to https://app.snowflake.com/
2. Login with username: HARSHITCODES
3. Click on your profile → "Change Password"
4. Generate a strong password (use password manager)
5. Update local .env file immediately

# Method 2: Via SQL
ALTER USER HARSHITCODES SET PASSWORD = '<new-strong-password>';
```

#### 1.2 Regenerate DeepSeek API Key

```bash
1. Go to https://platform.deepseek.com/api_keys
2. Login to your account
3. Revoke the exposed key: ***REDACTED_DEEPSEEK_API_KEY***
4. Generate a new API key
5. Update local .env file immediately
```

#### 1.3 Update Local .env File

```bash
cd /Users/harshitchoudhary/Desktop/lyzr-hackathon

# Create new .env with updated credentials
cat > .env << 'EOF'
# Snowflake Credentials
SNOWFLAKE_ACCOUNT=FHWELTT-XS07400
SNOWFLAKE_USER=HARSHITCODES
SNOWFLAKE_PASSWORD=<NEW_PASSWORD_HERE>
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=SNOWFLAKE_LEARNING_DB
SNOWFLAKE_SCHEMA=PUBLIC
SNOWFLAKE_ROLE=ACCOUNTADMIN

# DeepSeek API
DEEPSEEK_API_KEY=<NEW_API_KEY_HERE>

# Never commit this file!
EOF

chmod 600 .env  # Restrict permissions
```

---

### Phase 2: Clean Git History (Within 2 hours)

#### Option A: Using BFG Repo-Cleaner (Recommended)

```bash
cd /Users/harshitchoudhary/Desktop/lyzr-hackathon

# Make the cleanup script executable
chmod +x cleanup_secrets.sh

# Run the cleanup script
./cleanup_secrets.sh

# Follow the prompts
```

#### Option B: Manual Git Filter-Repo

```bash
# Install git-filter-repo
brew install git-filter-repo

# Create a backup first!
cp -r . ../lyzr-hackathon-backup

# Remove specific strings from history
git filter-repo --replace-text <(cat <<EOF
***REDACTED_DEEPSEEK_API_KEY***==>***REMOVED***
***REDACTED_PASSWORD***==>***REMOVED***
EOF
)

# Force push to remote
git push origin --force --all
git push origin --force --tags
```

---

### Phase 3: Verify Cleanup

```bash
# Search for exposed secrets in current files
cd /Users/harshitchoudhary/Desktop/lyzr-hackathon
grep -r "***REDACTED_DEEPSEEK_API_KEY***" .
grep -r "***REDACTED_PASSWORD***" .

# Search in Git history
git log --all --full-history --source -S "***REDACTED_DEEPSEEK_API_KEY***"
git log --all --full-history --source -S "***REDACTED_PASSWORD***"

# Should return no results!
```

---

### Phase 4: Force Push Changes

```bash
cd /Users/harshitchoudhary/Desktop/lyzr-hackathon

# Force push to overwrite remote history
git push origin main --force

# Force push all branches
git push origin --force --all

# Force push tags
git push origin --force --tags
```

---

## Files to Update

Update these files to use environment variables instead of hardcoded credentials:

### 1. `code/notebooks/superscan_snowflake_demo.py`

```python
# ❌ Before (line 127)
DEEPSEEK_API_KEY = "***REDACTED_DEEPSEEK_API_KEY***"

# ✅ After
import os
from dotenv import load_dotenv
load_dotenv()
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
```

### 2. `code/notebooks/test_superscan_flow.py`

```python
# ❌ Before (line 66)
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', '***REDACTED_DEEPSEEK_API_KEY***')

# ✅ After
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
if not DEEPSEEK_API_KEY:
    raise ValueError("DEEPSEEK_API_KEY environment variable not set")
```

---

## Preventive Measures

### 1. Update .gitignore

```bash
cd /Users/harshitchoudhary/Desktop/lyzr-hackathon

# Ensure .env files are ignored
cat >> .gitignore << 'EOF'

# Environment variables
.env
.env.*
*.env
!.env.example

# Secrets
secrets/
*.key
*.pem
*.p12
*.pfx

# Credentials
credentials.json
service-account.json
EOF

git add .gitignore
git commit -m "security: Update .gitignore to prevent credential leaks"
```

### 2. Create .env.example Template

```bash
cat > .env.example << 'EOF'
# Snowflake Configuration
SNOWFLAKE_ACCOUNT=your-account-here
SNOWFLAKE_USER=your-username
SNOWFLAKE_PASSWORD=your-password-here
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=your-database
SNOWFLAKE_SCHEMA=PUBLIC
SNOWFLAKE_ROLE=your-role

# API Keys
DEEPSEEK_API_KEY=your-deepseek-key-here
EOF

git add .env.example
git commit -m "docs: Add .env.example template"
```

### 3. Install Git Secrets Scanner

```bash
# Install gitleaks
brew install gitleaks

# Scan repository
cd /Users/harshitchoudhary/Desktop/lyzr-hackathon
gitleaks detect --verbose

# Add pre-commit hook
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
gitleaks protect --staged --verbose
EOF

chmod +x .git/hooks/pre-commit
```

### 4. Add GitHub Secret Scanning

1. Go to: https://github.com/harshit-codes/lyzr-hackathon/settings/security_analysis
2. Enable: **Secret scanning**
3. Enable: **Push protection**

---

## Audit Checklist

- [ ] ✅ Snowflake password rotated
- [ ] ✅ DeepSeek API key regenerated
- [ ] ✅ Local .env file updated with new credentials
- [ ] ✅ Git history cleaned (no secrets found)
- [ ] ✅ Force pushed to GitHub
- [ ] ✅ .gitignore updated
- [ ] ✅ .env.example created
- [ ] ✅ Gitleaks installed and scanning
- [ ] ✅ GitHub secret scanning enabled
- [ ] ✅ All hardcoded secrets replaced with env vars
- [ ] ✅ Verified no secrets in current codebase
- [ ] ✅ Notified collaborators (if any)

---

## Post-Incident Actions

### 1. Review Snowflake Access Logs

```sql
-- Login to Snowflake
USE ROLE ACCOUNTADMIN;

-- Check recent login history
SELECT 
    USER_NAME,
    CLIENT_IP,
    REPORTED_CLIENT_TYPE,
    LOGIN_TIME,
    IS_SUCCESS
FROM SNOWFLAKE.ACCOUNT_USAGE.LOGIN_HISTORY
WHERE USER_NAME = 'HARSHITCODES'
  AND LOGIN_TIME > DATEADD(day, -7, CURRENT_TIMESTAMP())
ORDER BY LOGIN_TIME DESC;

-- Check for unusual query activity
SELECT 
    USER_NAME,
    QUERY_TEXT,
    EXECUTION_STATUS,
    QUERY_TYPE,
    START_TIME
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE USER_NAME = 'HARSHITCODES'
  AND START_TIME > DATEADD(day, -7, CURRENT_TIMESTAMP())
ORDER BY START_TIME DESC
LIMIT 100;
```

### 2. Review DeepSeek API Usage

```bash
# Check API usage dashboard
# Look for:
# - Unusual spike in requests
# - Requests from unknown IPs
# - Failed authentication attempts
```

### 3. Enable MFA (Multi-Factor Authentication)

**Snowflake**:
```sql
-- Enable MFA for your user
ALTER USER HARSHITCODES SET 
    MUST_CHANGE_PASSWORD = TRUE,
    MINS_TO_UNLOCK = 15,
    LOGIN_NAME = 'HARSHITCODES';

-- Enroll in MFA via Snowsight UI
```

**DeepSeek**:
- Enable 2FA in account settings if available

---

## Communication

### For Solo Developers

Update this README section:

```markdown
## Security Update (October 14, 2025)

Credentials were accidentally exposed in Git history and have been:
- ✅ Rotated immediately
- ✅ Removed from Git history
- ✅ Secured with proper environment variable handling

All credentials in commit history are now invalid.
```

### For Team Projects

Send this message to all collaborators:

```
Subject: URGENT: Repository Security Incident - Action Required

Team,

We've experienced a security incident where credentials were exposed 
in our Git history. I've taken the following actions:

1. ✅ Rotated all exposed credentials
2. ✅ Cleaned Git history
3. ✅ Force-pushed cleaned history to GitHub

ACTION REQUIRED from you:

1. DELETE your local repository
2. RE-CLONE from GitHub:
   git clone https://github.com/harshit-codes/lyzr-hackathon.git
3. Update your .env file with the new credentials (I'll DM you)
4. Never commit the .env file

DO NOT try to pull/rebase your existing repository - it won't work 
due to the history rewrite.

Questions? Ping me immediately.

Thanks,
Harshit
```

---

## Lessons Learned

### What Went Wrong

1. ❌ Hardcoded credentials in source files
2. ❌ `.env` file not in `.gitignore` from the start
3. ❌ No pre-commit hooks to prevent secret commits
4. ❌ No code review process before pushing

### How to Prevent This

1. ✅ **Always** use environment variables
2. ✅ Add `.env` to `.gitignore` **before** first commit
3. ✅ Use `.env.example` as a template
4. ✅ Install `gitleaks` as pre-commit hook
5. ✅ Enable GitHub secret scanning
6. ✅ Use credential managers (1Password, AWS Secrets Manager)
7. ✅ Never commit credentials, even temporarily
8. ✅ Review diffs before committing

---

## Resources

- [GitHub Secret Scanning](https://docs.github.com/en/code-security/secret-scanning)
- [BFG Repo-Cleaner](https://rtyley.github.io/bfg-repo-cleaner/)
- [Gitleaks](https://github.com/gitleaks/gitleaks)
- [GitGuardian](https://www.gitguardian.com/)
- [OWASP Secrets Management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)

---

## Support

If you need help:
1. Snowflake Support: https://community.snowflake.com/
2. GitHub Security: https://github.com/security
3. GitGuardian: https://dashboard.gitguardian.com/

---

**Status**: 🚨 ACTIVE INCIDENT - Requires immediate action  
**Priority**: P0 - Critical  
**Owner**: Harshit Krishna Choudhary  
**Last Updated**: October 14, 2025
