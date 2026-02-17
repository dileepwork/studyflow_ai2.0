# 🚀 Quick Deploy to Vercel - Cheat Sheet

## ⚡ TL;DR - Deploy in 3 Steps

### 1️⃣ Get FREE Gemini API Key (30 seconds)
```
🔗 https://makersuite.google.com/app/apikey
   → Sign in → Create API Key → Copy it
```

### 2️⃣ Deploy (1 command)
```powershell
npx vercel
```

### 3️⃣ Add API Key to Vercel
```powershell
vercel env add GEMINI_API_KEY
# Paste your key → Select all environments
vercel --prod
```

**Done! Your app is live! 🎉**

---

## 📊 What Was Optimized

| Before | After | Saved |
|--------|-------|-------|
| 150 MB | 20 MB | **130 MB** ✅ |

**Key Changes:**
- ❌ Removed spaCy (60MB) → ✅ Gemini API
- ❌ Removed NetworkX (15MB) → ✅ Custom code
- ❌ Removed NumPy (25MB) → ✅ Pure Python
- ❌ Removed Firebase (10MB) → ✅ Optional

---

## 🔍 Quick Test After Deploy

```powershell
# Test API health
curl https://your-app.vercel.app/api/health

# Should return:
# {"status": "healthy", "message": "API is running!"}
```

---

## 🐛 Common Issues & Fixes

### "GEMINI_API_KEY not set"
```powershell
vercel env add GEMINI_API_KEY
# Then redeploy:
vercel --prod
```

### Build Fails
```powershell
# Test locally first:
cd frontend
npm install
npm run build

# Check for errors, then redeploy
```

### 404 on Routes
- Check `vercel.json` exists in root
- Verify `dist/` folder has `index.html`
- Redeploy: `vercel --prod`

---

## 📁 File Structure (Optimized)

```
studyflowai/
├── api/
│   ├── index.py              # Flask API
│   ├── utils.py              # Gemini NLP
│   ├── processor.py          # Lightweight graph
│   └── requirements.txt      # 5 packages only!
├── frontend/
│   ├── dist/                 # Auto-built by Vercel
│   └── package.json          # No Firebase!
├── vercel.json               # Deployment config
├── package.json              # Build script
└── .env.example              # Template
```

---

## 💡 Pro Tips

### Faster Deploys
```powershell
# Skip preview, deploy to production directly
vercel --prod
```

### Check Deployment Logs
```powershell
vercel logs https://your-app.vercel.app
```

### Environment Variables
```powershell
# List all env vars
vercel env ls

# Remove a var
vercel env rm GEMINI_API_KEY

# Pull env to local .env
vercel env pull
```

---

## 🎯 API Endpoints

### Health Check
```
GET /api/health
```

### Analyze Syllabus
```
POST /api/analyze
Form Data:
  - file: PDF file
  - weeks: 4
  - hours: 10
  - level: "Beginner"
```

### Chat with Mentor
```
POST /api/chat
JSON:
  { "topic": "...", "message": "..." }
```

---

## 💰 Costs

**Everything is FREE:**
- ✅ Vercel Hobby: $0/month (100GB bandwidth)
- ✅ Gemini API: $0/month (1500 req/day)
- ✅ Total: **$0/month** 🎉

---

## 🔗 Important Links

- **Get API Key:** https://makersuite.google.com/app/apikey
- **Vercel Dashboard:** https://vercel.com/dashboard
- **Deployment Guide:** See `DEPLOYMENT_STEPS.md`
- **Optimization Report:** See `OPTIMIZATION_REPORT.md`

---

## 🚀 One-Line Deploy

```powershell
# Complete setup in one go:
./deploy.ps1
```

---

## ✅ Deployment Checklist

- [ ] Get Gemini API key
- [ ] Run `vercel` to deploy
- [ ] Add `GEMINI_API_KEY` env var
- [ ] Redeploy with `vercel --prod`
- [ ] Test `/api/health` endpoint
- [ ] Upload test PDF on frontend
- [ ] Share your link! 🎉

---

**Deployment Time:** ~5 minutes  
**Size:** ~20MB (well under 250MB limit)  
**Status:** ✅ Ready to Go!
