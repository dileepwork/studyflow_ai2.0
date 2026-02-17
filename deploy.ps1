# ===================================
# 🚀 Quick Deployment Script
# ===================================

Write-Host "`n🎓 StudyFlow AI - Vercel Deployment Helper`n" -ForegroundColor Cyan

# Check if .env exists
if (Test-Path ".env") {
    Write-Host "✅ .env file found" -ForegroundColor Green
} else {
    Write-Host "⚠️  No .env file found. Creating one...`n" -ForegroundColor Yellow
    
    Write-Host "📋 To get your FREE Gemini API key:" -ForegroundColor Cyan
    Write-Host "   1. Visit: https://makersuite.google.com/app/apikey"
    Write-Host "   2. Sign in with Google"
    Write-Host "   3. Click 'Create API Key'"
    Write-Host "   4. Copy the key (starts with 'AIza...')`n"
    
    $apiKey = Read-Host "Paste your Gemini API key here"
    
    if ($apiKey) {
        "GEMINI_API_KEY=$apiKey" | Out-File -FilePath ".env" -Encoding UTF8
        Write-Host "`n✅ .env file created successfully!`n" -ForegroundColor Green
    } else {
        Write-Host "`n❌ No API key provided. Please create .env manually.`n" -ForegroundColor Red
        exit 1
    }
}

# Check dependencies
Write-Host "📦 Checking deployment readiness...`n" -ForegroundColor Cyan

# Check if vercel.json exists
if (Test-Path "vercel.json") {
    Write-Host "✅ vercel.json found" -ForegroundColor Green
} else {
    Write-Host "❌ vercel.json missing!" -ForegroundColor Red
}

# Check if api/requirements.txt exists
if (Test-Path "api/requirements.txt") {
    Write-Host "✅ requirements.txt found" -ForegroundColor Green
    
    # Show size estimate
    $content = Get-Content "api/requirements.txt"
    Write-Host "📊 Dependencies: $($content.Count) packages" -ForegroundColor Cyan
} else {
    Write-Host "❌ api/requirements.txt missing!" -ForegroundColor Red
}

# Check if frontend builds
if (Test-Path "frontend/package.json") {
    Write-Host "✅ frontend/package.json found`n" -ForegroundColor Green
} else {
    Write-Host "❌ frontend/package.json missing!`n" -ForegroundColor Red
}

# Next steps
Write-Host "════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "📋 Next Steps:`n" -ForegroundColor Yellow
Write-Host "1️⃣  Test locally (optional):" -ForegroundColor White
Write-Host "   cd api && python index.py" -ForegroundColor Gray
Write-Host "   cd frontend && npm run dev`n" -ForegroundColor Gray

Write-Host "2️⃣  Deploy to Vercel:" -ForegroundColor White
Write-Host "   npm install -g vercel" -ForegroundColor Gray
Write-Host "   vercel login" -ForegroundColor Gray
Write-Host "   vercel`n" -ForegroundColor Gray

Write-Host "3️⃣  Add API key to Vercel:" -ForegroundColor White
Write-Host "   vercel env add GEMINI_API_KEY" -ForegroundColor Gray
Write-Host "   (Then paste your key)`n" -ForegroundColor Gray

Write-Host "4️⃣  Redeploy with env vars:" -ForegroundColor White
Write-Host "   vercel --prod`n" -ForegroundColor Gray

Write-Host "════════════════════════════════════════════" -ForegroundColor Cyan

$deploy = Read-Host "`nDo you want to deploy now? (y/n)"

if ($deploy -eq "y" -or $deploy -eq "Y") {
    Write-Host "`n🚀 Starting deployment...`n" -ForegroundColor Green
    
    # Check if Vercel CLI is installed
    $vercelCheck = Get-Command vercel -ErrorAction SilentlyContinue
    
    if (-not $vercelCheck) {
        Write-Host "📦 Installing Vercel CLI..." -ForegroundColor Yellow
        npm install -g vercel
    }
    
    Write-Host "`n🔐 Logging into Vercel..." -ForegroundColor Cyan
    vercel login
    
    Write-Host "`n📤 Deploying project..." -ForegroundColor Cyan
    vercel
    
    Write-Host "`n✅ Deployment initiated!" -ForegroundColor Green
    Write-Host "`n⚠️  IMPORTANT: Don't forget to add GEMINI_API_KEY to Vercel!" -ForegroundColor Yellow
    Write-Host "   vercel env add GEMINI_API_KEY`n" -ForegroundColor Gray
    
} else {
    Write-Host "`n📖 Run 'vercel' when you're ready to deploy!`n" -ForegroundColor Cyan
}

Write-Host "📚 For detailed guide, see: DEPLOYMENT_STEPS.md`n" -ForegroundColor Cyan
