# 🚀 Vercel Deployment Guide - Optimized for <250MB

## ✅ What Changed for Lightweight Deployment

**Before:** ~150MB (spaCy model, networkx, heavy dependencies)  
**After:** ~20MB (Gemini API, lightweight Python packages)

### Key Optimizations:
1. ✅ Replaced spaCy NLP model with Gemini API (saves ~60MB)
2. ✅ Removed networkx, numpy, pydantic (saves ~40MB)
3. ✅ Implemented custom graph algorithms (lightweight)
4. ✅ Added API-based AI features for better performance

---

## 📋 Prerequisites

1. **Vercel Account** - [Sign up free](https://vercel.com/signup)
2. **Gemini API Key** - [Get free key](https://makersuite.google.com/app/apikey) (100% free tier available)
3. **Git** installed on your system

---

## 🔑 Step 1: Get Your Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click **"Create API Key"**
4. Copy the key (starts with `AIza...`)

**Why Gemini?**
- ✅ 100% FREE tier (60 requests/minute)
- ✅ Powerful NLP without heavy models
- ✅ No credit card required
- ✅ Fast and reliable

---

## 🚀 Step 2: Deploy to Vercel

### Option A: Using Vercel CLI (Recommended)

```powershell
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy from project root
cd c:\Users\Dileep\studyflowai
vercel
```

**During deployment, you'll be asked:**
- Set up project? → **Y**
- Which scope? → Select your account
- Link to existing project? → **N**
- Project name? → **studyflowai** (or your choice)
- Directory location? → `.` (current directory)
- Modify settings? → **N**

### Option B: Using Vercel Dashboard

1. Go to [vercel.com/new](https://vercel.com/new)
2. Import your Git repository OR upload project folder
3. Vercel will auto-detect settings from `vercel.json`
4. Click **"Deploy"**

---

## 🔧 Step 3: Add Environment Variable

**CRITICAL:** Add your Gemini API key to Vercel:

### Via Dashboard:
1. Go to your project on Vercel
2. Click **Settings** → **Environment Variables**
3. Add:
   - **Name:** `GEMINI_API_KEY`
   - **Value:** Your API key from Step 1
   - **Environment:** Production + Preview + Development
4. Click **Save**
5. **Redeploy** the project (Settings → Deployments → menu → Redeploy)

### Via CLI:
```powershell
vercel env add GEMINI_API_KEY
# Paste your API key when prompted
# Select all environments (Production, Preview, Development)

# Redeploy with new env
vercel --prod
```

---

## ✅ Step 4: Test Your Deployment

Once deployed, Vercel will give you a URL like:
**`https://studyflowai-xyz.vercel.app`**

### Test the API:
```powershell
# Test health endpoint
curl https://your-url.vercel.app/api/health

# Should return: {"status": "healthy", ...}
```

### Test the Frontend:
1. Open the URL in your browser
2. Upload a sample syllabus
3. Verify that topics are extracted and schedules are generated

---

## 📊 Deployment Size Check

After deployment, check the size:
```powershell
vercel inspect https://your-url.vercel.app
```

**Expected size:** 15-25 MB ✅  
**Vercel limit:** 250 MB ✅

---

## 🐛 Troubleshooting

### "GEMINI_API_KEY not set" Error
- Make sure you added the environment variable
- Redeploy after adding env vars
- Check variable name is exactly: `GEMINI_API_KEY`

### "Cold start timeout"
- First request after inactivity may be slow (2-5 seconds)
- This is normal for serverless functions
- Subsequent requests will be fast

### Build Fails
```powershell
# Check deployment logs
vercel logs https://your-url.vercel.app

# Common fixes:
# 1. Make sure vercel.json is in root directory
# 2. Check that api/requirements.txt has correct packages
# 3. Verify vercel-build script in package.json
```

### Frontend 404 Error
- Ensure `dist/` folder is created during build
- Check `vercel.json` routes configuration
- Verify frontend builds successfully locally:
  ```powershell
  cd frontend
  npm install
  npm run build
  ```

---

## 🔄 Update Deployment

```powershell
# Make changes to your code
git add .
git commit -m "Updated features"
git push

# Redeploy
vercel --prod
```

Or just push to GitHub if you connected your repo!

---

## 💰 Cost Breakdown

**Total Cost: $0** 🎉

- Vercel Hobby Plan: FREE (100GB bandwidth/month)
- Gemini API: FREE (60 requests/minute, 1500/day)
- Storage: FREE (Vercel serverless)

---

## 📚 Project Structure

```
studyflowai/
├── api/
│   ├── index.py          # Flask API (serverless function)
│   ├── utils.py          # PDF parsing + Gemini NLP
│   ├── processor.py      # Scheduling logic
│   └── requirements.txt  # Lightweight dependencies
├── frontend/
│   ├── src/              # React app
│   └── dist/             # Built frontend (auto-generated)
├── vercel.json           # Vercel configuration
├── package.json          # Root build script
└── .env                  # Local env vars (not deployed)
```

---

## 🎯 Next Steps

1. ✅ Share your deployment URL
2. 🎨 Customize the UI in `frontend/src/`
3. 📊 Monitor usage on Vercel dashboard
4. 🔧 Add more features to the AI mentor
5. 📱 Make it mobile-responsive (already optimized!)

---

## 🆘 Need Help?

- [Vercel Documentation](https://vercel.com/docs)
- [Gemini API Docs](https://ai.google.dev/docs)
- Check deployment logs: `vercel logs`

---

**Deployment Size: ~20MB ✅**  
**Vercel Limit: 250MB ✅**  
**You're all set! 🚀**
