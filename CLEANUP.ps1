# Delete these unnecessary files for clean GitHub push

# PowerShell Script - Run in: c:\Users\Lenovo\diseasesdetction

Write-Host "🧹 Cleaning up project for GitHub..." -ForegroundColor Green

# Documentation files (for viva only)
Remove-Item -Force -ErrorAction SilentlyContinue VIVA_GUIDE.md
Remove-Item -Force -ErrorAction SilentlyContinue VIVA_CHEAT_SHEET.md
Remove-Item -Force -ErrorAction SilentlyContinue FIXES_COMPLETE.md
Remove-Item -Force -ErrorAction SilentlyContinue FINAL_STATUS_FIXED.md
Remove-Item -Force -ErrorAction SilentlyContinue FINAL_STATUS.md
Remove-Item -Force -ErrorAction SilentlyContinue QUICK_START.md
Remove-Item -Force -ErrorAction SilentlyContinue STATUS.md
Remove-Item -Force -ErrorAction SilentlyContinue SYSTEM_STATUS.md

# Duplicate code (keep only app/ for frontend)
Remove-Item -Recurse -Force -ErrorAction SilentlyContinue nextjs-app/
Remove-Item -Recurse -Force -ErrorAction SilentlyContinue model/
Remove-Item -Force -ErrorAction SilentlyContinue server.js
Remove-Item -Force -ErrorAction SilentlyContinue run.sh

# Test files
Remove-Item -Force -ErrorAction SilentlyContinue test_api.py

# Archive/backup
Remove-Item -Recurse -Force -ErrorAction SilentlyContinue archive/
Remove-Item -Force -ErrorAction SilentlyContinue archive.zip

# Update main README (optional)
Remove-Item -Force -ErrorAction SilentlyContinue README.md
Rename-Item -Force README_CLEAN.md -NewName README.md

# Update .gitignore
Remove-Item -Force -ErrorAction SilentlyContinue .gitignore
Rename-Item -Force .gitignore_clean -NewName .gitignore

Write-Host "✅ Cleanup complete!" -ForegroundColor Green
Write-Host "📁 Only essential files remain for GitHub" -ForegroundColor Cyan
Write-Host ""
Write-Host "Remaining structure:" -ForegroundColor Yellow
Write-Host "  ├── app/" -ForegroundColor Gray
Write-Host "  ├── lib/" -ForegroundColor Gray
Write-Host "  ├── data/" -ForegroundColor Gray
Write-Host "  ├── public/" -ForegroundColor Gray
Write-Host "  ├── README.md" -ForegroundColor Gray
Write-Host "  ├── package.json" -ForegroundColor Gray
Write-Host "  ├── next.config.js" -ForegroundColor Gray
Write-Host "  ├── tailwind.config.js" -ForegroundColor Gray
Write-Host "  └── .gitignore" -ForegroundColor Gray
