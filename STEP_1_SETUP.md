# 🚀 Level 5, Step 1: Setup Instructions

## ✅ What Was Completed

All files have been created and security measures are in place! 

## 📋 Next Steps (Do This Now!)

### Step 1: Create Your .env File

Copy the template to create your actual environment file:

**On Windows PowerShell:**
```powershell
Copy-Item .env.example .env
```

**Or manually:**
1. Copy `.env.example`
2. Rename the copy to `.env`

### Step 2: Get Your OpenAI API Key

1. Go to: https://platform.openai.com/signup
2. Sign up or log in
3. Navigate to: https://platform.openai.com/api-keys
4. Click "Create new secret key"
5. Copy the key (starts with `sk-`)

### Step 3: Add API Key to .env

Open `.env` file and replace the placeholder:

```
OPENAI_API_KEY=sk-your-actual-key-here
```

**⚠️ IMPORTANT:** Never commit this file to Git!

### Step 4: Set Spending Limits (Recommended)

1. Go to: https://platform.openai.com/account/billing
2. Click "Set usage limits"
3. Set hard limit: $10
4. Set soft limit: $5 (you'll get email alert)

### Step 5: Test Your Setup

Run the setup test:

```powershell
python ai/setup_openai.py
```

**Expected output:**
- ✅ API key loaded successfully!
- 🤖 AI Response: "Hello! OpenAI is working!"
- 📊 Tokens Used: ~50
- 💰 Estimated Cost: ~$0.0001 USD

### Step 6: Try Your First Chatbot!

Run the interactive chatbot:

```powershell
python ai/simple_chat.py
```

Or run a demo:

```powershell
python ai/simple_chat.py --demo
```

---

## 🔐 Security Verification

Before you start, verify security:

```powershell
# This should output: .env
git check-ignore .env

# This should NOT show .env file
git status
```

---

## 🆘 Troubleshooting

### "API key not found"
- Make sure you created `.env` file (not `.env.txt`)
- Check that `.env` is in the root directory
- Verify the key starts with `sk-`

### "Module not found: openai"
- Make sure virtual environment is activated
- Run: `pip install openai python-dotenv`

### "Incorrect API key"
- Double-check you copied the full key
- No extra spaces before/after the key
- Generate a new key if needed

---

## 📊 What You'll Learn

By completing Step 1, you'll understand:
- ✅ How to securely store API keys
- ✅ How to make OpenAI API calls
- ✅ Token usage and costs
- ✅ Building conversational AI
- ✅ System prompts and context

---

## 💰 Cost Estimate

**For Step 1 testing:**
- Setup test: ~$0.0001
- Simple chat (10 messages): ~$0.001
- Demo conversation: ~$0.0005
- **Total: Less than $0.01**

**You got this!** 🚀

---

Need help? Check `SECURITY_CHECKLIST.md` for safety guidelines.
