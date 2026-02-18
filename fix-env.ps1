# ⚡ Quick Fix Script for Environment Variables
# Run this if you're getting "Analysis failed. Server error"

Write-Host "`n🔧 StudyFlow AI - Environment Variable Fix`n" -ForegroundColor Cyan

$apiKey = "AIzaSyCCowz-ePIqQemP3uJLLzklxaf4WZBsS18"

Write-Host "📋 Current Environment Variables:`n" -ForegroundColor Yellow
vercel env ls

Write-Host "`n⚠️  If you see GEMINI_API_KEY only for 'Production', that's the problem!`n" -ForegroundColor Red

Write-Host "✅ SOLUTION:

1. Open this URL in your browser:
   https://vercel.com/dileeps-projects-a35b7e09/studyflowai/settings/environment-variables

2. Click on 'GEMINI_API_KEY' to edit it

3. Check ALL three boxes:
   ☑️ Production
   ☑️ Preview
   ☑️ Development

4. Click 'Save'

5. Go to Deployments tab and click 'Redeploy' on the latest deployment

OR run this command to redeploy production:
   vercel --prod

" -ForegroundColor Green

$choice = Read-Host "Do you want me to redeploy production now? (y/n)"

if ($choice -eq "y" -or $choice -eq "Y") {
    Write-Host "`n🚀 Redeploying to production...`n" -ForegroundColor Cyan
    vercel --prod
    
    Write-Host "`n✅ Deployment initiated!`n" -ForegroundColor Green
    Write-Host "⏳ Wait 1-2 minutes, then test at:" -ForegroundColor Yellow
    Write-Host "   https://studyflowai-self.vercel.app`n" -ForegroundColor Cyan
}
else {
    Write-Host "`n📖 Follow the steps above to fix the issue manually.`n" -ForegroundColor Cyan
}

Write-Host "📚 For detailed troubleshooting, see: TROUBLESHOOTING.md`n" -ForegroundColor Cyan
