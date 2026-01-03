# 🔐 Security Checklist - Level 5

## ⚠️ CRITICAL: Run Before Every Git Push!

### ✅ Before Committing Files:

- [ ] `.env` file exists locally (contains your API key)
- [ ] `.env` is listed in `.gitignore`
- [ ] `.env.example` exists (safe template without real key)
- [ ] No API keys are hardcoded in any `.py` files

**Verification Command:**
```powershell
git check-ignore .env
```
**Expected output:** `.env` (means it's being ignored ✅)

---

### ✅ Before Running `git add`:

```powershell
# Check what will be staged
git status
```

**❌ DANGER if you see:**
- `.env` in the list
- Any file with `API_KEY` in the name

**✅ SAFE if you see:**
- `.env.example`
- `.gitignore`
- Python files (`.py`)

---

### ✅ Before Running `git commit`:

```powershell
# Review what will be committed
git diff --cached
```

**Look for:**
- ❌ Any line with `sk-` followed by long string (OpenAI key)
- ❌ `OPENAI_API_KEY = "sk-..."`
- ❌ Any hardcoded secrets

---

### ✅ Before Running `git push`:

```powershell
# Final check - see all files in commit
git ls-files

# Check if .env would be pushed
git ls-files | findstr ".env"
```

**Expected output:** Should only show `.env.example`, never `.env`

---

## 🚨 Emergency: If You Accidentally Commit .env

### **Before Pushing (Easy Fix):**
```powershell
# Unstage the file
git reset HEAD .env

# Verify it's removed
git status
```

### **After Pushing (Serious Fix):**

1. **Immediately revoke your API key:**
   - Go to: https://platform.openai.com/api-keys
   - Delete the exposed key
   - Generate a new key

2. **Update your local .env:**
   ```
   OPENAI_API_KEY=new_key_here
   ```

3. **Remove from Git history:**
   ```powershell
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch .env" \
     --prune-empty --tag-name-filter cat -- --all
   
   git push origin --force --all
   ```

4. **Or make repo private temporarily**

---

## 🔍 Regular Security Audit

### Weekly Checks:

```powershell
# 1. Verify .env is ignored
git check-ignore .env

# 2. Check for any secrets in tracked files
git grep -i "api.key"
git grep -i "sk-"

# 3. Review .gitignore
cat .gitignore
```

---

## ✅ Safe Files to Commit

**Always safe:**
- `.env.example` - Template without real keys
- `.gitignore` - Protection rules
- `*.py` files - If they load from environment
- `requirements.txt` - Library list
- Documentation files

**Never commit:**
- `.env` - Contains real API key
- `*.key` files
- `secrets.json`
- Any file with real credentials

---

## 📱 GitHub Security Features

**GitHub automatically:**
- Scans commits for API keys
- Disables exposed OpenAI keys
- Sends email alerts
- Shows security warnings

**But don't rely on this! Prevent exposure in the first place.**

---

## 💡 Best Practices

1. **Use environment variables for ALL secrets**
2. **Never hardcode API keys**
3. **Add `.env` to `.gitignore` FIRST**
4. **Create `.env.example` as template**
5. **Review commits before pushing**
6. **Rotate keys regularly**
7. **Use different keys for dev/production**

---

## 🎯 Quick Pre-Push Checklist

```
[ ] Ran: git status
[ ] Verified: .env NOT in the list
[ ] Ran: git check-ignore .env
[ ] Confirmed: .env is ignored
[ ] Reviewed: git diff --cached
[ ] No secrets visible
[ ] Ready to push safely!
```

---

## 📞 Questions?

If unsure about anything:
1. **DON'T push** until certain
2. Run the verification commands above
3. Ask for help if needed

**Better to be safe than expose your API key!** 🔐

---

Generated: Level 5, Step 1
Last Updated: December 30, 2025
