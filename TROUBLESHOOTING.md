# 🔧 Troubleshooting Guide - StudyFlow AI

## ❌ Error: "Analysis failed. Server error."

### **Problem:**
When you upload a syllabus PDF, you see an error:
```
Error: Analysis failed. Server error.
Check console for details.
```

### **Root Cause:**
The `GEMINI_API_KEY` environment variable is not set for all deployment environments in Vercel. It's only set for Production, but preview/development deployments don't have access to it.

---

## ✅ **Solution 1: Add Environment Variable for All Environments (Recommended)**

### **Step 1: Go to Vercel Dashboard**
Open this URL in your browser:
```
https://vercel.com/dileeps-projects-a35b7e09/studyflowai/settings/environment-variables
```

Or:
1. Go to https://vercel.com/dashboard
2. Click on your **studyflowai** project
3. Click **Settings** (top tab)
4. Click **Environment Variables** (left sidebar)

### **Step 2: Edit GEMINI_API_KEY**
1. Find the **GEMINI_API_KEY** variable
2. Click on it to edit
3. **Check ALL THREE environments:**
   - ✅ Production
   - ✅ Preview
   - ✅ Development
4. Click **Save**

### **Step 3: Redeploy**
After saving, you need to redeploy:

**Option A: Via Dashboard:**
1. Go to **Deployments** tab
2. Find the latest deployment
3. Click the 3-dot menu (⋯) → **Redeploy**
4. Confirm

**Option B: Via CLI:**
```powershell
cd c:\Users\Dileep\studyflowai
vercel --prod
```

### **Step 4: Test**
1. Wait 1-2 minutes for deployment to complete
2. Open https://studyflowai-self.vercel.app
3. Upload a test PDF
4. Should work now! ✅

---

## ✅ **Solution 2: Use Production Deployment Directly (Quick Fix)**

If you're seeing a preview URL like:
```
https://studyflowai-xyz-preview.vercel.app
```

**Use the production URL instead:**
```
https://studyflowai-self.vercel.app
```

Production has the API key configured and should work.

---

## ✅ **Solution 3: Add Environment Variable via CLI**

If you prefer using the command line:

### **For Production:**
```powershell
echo AIzaSyCCowz-ePIqQemP3uJLLzklxaf4WZBsS18 | vercel env add GEMINI_API_KEY production
```

### **For Preview:**
```powershell
echo AIzaSyCCowz-ePIqQemP3uJLLzklxaf4WZBsS18 | vercel env add GEMINI_API_KEY preview
```

### **For Development:**
```powershell
echo AIzaSyCCowz-ePIqQemP3uJLLzklxaf4WZBsS18 | vercel env add GEMINI_API_KEY development
```

Then redeploy:
```powershell
vercel --prod
```

---

## 🧪 **Verify the Fix**

### **Test 1: Check API Health**
```powershell
Invoke-WebRequest -Uri "https://studyflowai-self.vercel.app/api/health" -UseBasicParsing
```

**Expected Response:**
```json
{
  "status": "healthy",
  "message": "API is running!",
  "timestamp": "2026-02-17"
}
```

### **Test 2: Upload a Sample Syllabus**
1. Go to https://studyflowai-self.vercel.app
2. Click "Upload Syllabus"
3. Upload `sample_syllabus.txt` (in project root)
4. Set weeks: 4, hours: 10, level: Beginner
5. Click "Analyze"
6. Should see topics and schedule! ✅

---

## 🔍 **Check Deployment Logs**

If still having issues, check Vercel logs:

```powershell
vercel logs https://studyflowai-self.vercel.app
```

**Look for:**
- ❌ `GEMINI_API_KEY not set` → Environment variable missing
- ❌ `Failed to import dependencies` → Python package issue
- ❌ `API quota exceeded` → Gemini API limit reached (unlikely)

---

## 📊 **Common Issues & Fixes**

### **Issue 1: "GEMINI_API_KEY not set"**
**Fix:** Add environment variable to all environments (see Solution 1)

### **Issue 2: "Cold start timeout"**
**Fix:** This is normal for serverless. Wait 5 seconds and try again.

### **Issue 3: "No topics extracted"**
**Possible Causes:**
- PDF is scanned image (not text-based)
- PDF is corrupted
- Gemini API error

**Fix:**
- Try a different PDF
- Check PDF has selectable text (not just an image)
- Check Gemini API quota: https://makersuite.google.com/app/apikey

### **Issue 4: "Analysis takes too long"**
**Fix:** 
- First request after deployment is slow (cold start)
- Subsequent requests are faster
- Large PDFs (>20 pages) take longer

### **Issue 5: Preview deployment doesn't work**
**Fix:** Use production URL instead: https://studyflowai-self.vercel.app

---

## 🔑 **Environment Variables Checklist**

Run this to verify environment variables are set:

```powershell
vercel env ls
```

**Expected Output:**
```
GEMINI_API_KEY    Encrypted    Production    ✅
GEMINI_API_KEY    Encrypted    Preview       ✅
GEMINI_API_KEY    Encrypted    Development   ✅
```

If you see only "Production", that's the problem!

---

## 🆘 **Still Not Working?**

### **Nuclear Option: Recreate Environment Variables**

1. **Remove existing variable:**
```powershell
vercel env rm GEMINI_API_KEY
# Confirm for all environments
```

2. **Re-add for all environments:**

Via Vercel Dashboard:
- Go to Settings → Environment Variables
- Click "Add New"
- Name: `GEMINI_API_KEY`
- Value: `AIzaSyCCowz-ePIqQemP3uJLLzklxaf4WZBsS18`
- Check ALL environments: Production, Preview, Development
- Click Save

3. **Force redeploy:**
```powershell
vercel --prod --force
```

4. **Wait 2 minutes and test**

---

## 📱 **Browser Console Debugging**

If error persists:

1. **Open browser DevTools** (F12)
2. Go to **Console** tab
3. Upload a PDF
4. Look for errors

**Common Console Errors:**

**Error:** `Failed to fetch`
- **Cause:** API endpoint unreachable
- **Fix:** Check Vercel deployment status

**Error:** `500 Internal Server Error`
- **Cause:** Backend Python error
- **Fix:** Check Vercel logs

**Error:** `CORS error`
- **Cause:** CORS not configured (shouldn't happen)
- **Fix:** Check `api/index.py` has `CORS(app)`

---

## ✅ **Quick Test Commands**

```powershell
# Test health endpoint
Invoke-WebRequest -Uri "https://studyflowai-self.vercel.app/api/health" -UseBasicParsing

# Check environment variables
vercel env ls

# View recent logs
vercel logs https://studyflowai-self.vercel.app

# Force production redeploy
vercel --prod --force

# Check deployment status
vercel ls
```

---

## 📚 **Additional Resources**

- **Vercel Dashboard:** https://vercel.com/dashboard
- **Gemini API Console:** https://makersuite.google.com/app/apikey
- **Project Settings:** https://vercel.com/dileeps-projects-a35b7e09/studyflowai/settings
- **Deployment Logs:** https://vercel.com/dileeps-projects-a35b7e09/studyflowai/deployments

---

## 🎯 **TL;DR - Quick Fix**

1. Go to: https://vercel.com/dileeps-projects-a35b7e09/studyflowai/settings/environment-variables
2. Edit `GEMINI_API_KEY`
3. Check **ALL** environments (Production, Preview, Development)
4. Save
5. Go to Deployments tab → Redeploy latest
6. Wait 2 minutes
7. Test at: https://studyflowai-self.vercel.app

**Done!** ✅
