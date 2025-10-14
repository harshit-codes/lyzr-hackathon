#!/bin/bash
# Script to remove sensitive data from Git history
# WARNING: This rewrites Git history. Make sure to coordinate with team!

set -e

echo "=================================="
echo "GIT SECRETS CLEANUP SCRIPT"
echo "=================================="
echo ""
echo "⚠️  WARNING: This will rewrite Git history!"
echo "⚠️  All collaborators will need to re-clone the repository!"
echo ""
read -p "Are you sure you want to continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Aborted."
    exit 1
fi

cd "$(dirname "$0")"

echo ""
echo "Step 1: Installing BFG Repo-Cleaner (if not installed)..."
if ! command -v bfg &> /dev/null; then
    if command -v brew &> /dev/null; then
        brew install bfg
    else
        echo "Please install BFG manually: https://rtyley.github.io/bfg-repo-cleaner/"
        exit 1
    fi
fi

echo ""
echo "Step 2: Creating backup..."
backup_dir="../lyzr-hackathon-backup-$(date +%Y%m%d_%H%M%S)"
cp -r . "$backup_dir"
echo "✓ Backup created at: $backup_dir"

echo ""
echo "Step 3: Creating secrets file for BFG..."
cat > secrets.txt << 'EOF'
***REDACTED_DEEPSEEK_API_KEY***
***REDACTED_PASSWORD***
SNOWFLAKE_PASSWORD=***REDACTED_PASSWORD***
DEEPSEEK_API_KEY=***REDACTED_DEEPSEEK_API_KEY***
EOF

echo ""
echo "Step 4: Running BFG to remove secrets from Git history..."
bfg --replace-text secrets.txt

echo ""
echo "Step 5: Running git reflog and garbage collection..."
git reflog expire --expire=now --all
git gc --prune=now --aggressive

echo ""
echo "Step 6: Removing secrets file..."
rm secrets.txt

echo ""
echo "Step 7: Updating files to use environment variables..."

# Update files with hardcoded secrets
files_to_update=(
    "code/notebooks/superscan_snowflake_demo.py"
    "code/notebooks/test_superscan_flow.py"
)

for file in "${files_to_update[@]}"; do
    if [ -f "$file" ]; then
        echo "  Updating $file..."
        sed -i '' 's/***REDACTED_DEEPSEEK_API_KEY***/\$\{DEEPSEEK_API_KEY\}/g' "$file"
    fi
done

echo ""
echo "Step 8: Ensuring .env is in .gitignore..."
if ! grep -q "^\.env$" .gitignore 2>/dev/null; then
    echo ".env" >> .gitignore
    echo "*.env" >> .gitignore
    echo ".env.*" >> .gitignore
    git add .gitignore
    git commit -m "security: Add .env files to .gitignore"
fi

echo ""
echo "=================================="
echo "✅ CLEANUP COMPLETE!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Review changes: git log --oneline -10"
echo "2. Force push to GitHub: git push origin --force --all"
echo "3. Force push tags: git push origin --force --tags"
echo "4. Rotate credentials immediately:"
echo "   - Change Snowflake password"
echo "   - Regenerate DeepSeek API key"
echo "5. Update .env file with new credentials"
echo "6. Notify all collaborators to re-clone the repository"
echo ""
echo "⚠️  OLD CREDENTIALS ARE NOW EXPOSED - ROTATE THEM IMMEDIATELY!"
echo ""
