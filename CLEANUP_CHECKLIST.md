# 🧹 Files to Remove (Unnecessary)

## Documentation (for viva only, remove for GitHub)
- [ ] VIVA_GUIDE.md
- [ ] VIVA_CHEAT_SHEET.md  
- [ ] FIXES_COMPLETE.md
- [ ] FINAL_STATUS_FIXED.md
- [ ] FINAL_STATUS.md
- [ ] QUICK_START.md
- [ ] STATUS.md
- [ ] SYSTEM_STATUS.md

## Duplicate/Alternative Code (keep only main app/)
- [ ] nextjs-app/ (entire folder - duplicate Next.js setup)
- [ ] model/ (old Python setup - logic moved to lib/predict.py)
- [ ] server.js (old Node server - use Next.js instead)
- [ ] public/app.js (old frontend - use Next.js instead)
- [ ] public/index.html (old frontend - use Next.js instead)
- [ ] public/styles.css (use TailwindCSS instead)

## Build/Cache Files
- [ ] .next/ (generated on build)
- [ ] node_modules/ (install with npm install)
- [ ] __pycache__/ (Python cache)
- [ ] *.pyc files

## Archive/Datasets
- [ ] archive/ (old dataset backup)
- [ ] archive.zip
- [ ] .kaggle/ (API credentials - add to .gitignore)

## Temporary/Test Files
- [ ] test_api.py (testing only)
- [ ] run.sh (Linux only, add npm/python scripts to package.json)

## Configuration Files (optional)
- [ ] design/ (architecture docs - can keep or remove)
- [ ] docker-compose.yml (keep if deploying with Docker)
- [ ] Dockerfile (keep if deploying with Docker)

## Keep These ✅
- ✅ app/ (Next.js frontend)
- ✅ lib/ (Python backend + model)
- ✅ data/ (knowledge base)
- ✅ public/ (favicons, manifest)
- ✅ package.json
- ✅ package-lock.json
- ✅ README.md (or README_CLEAN.md)
- ✅ tailwind.config.js
- ✅ next.config.js
- ✅ postcss.config.js
- ✅ .gitignore
- ✅ .env.example

---

## Total Removable: ~15 files/folders
## Total to Keep: ~10 files/folders
## Space Saved: ~500MB (mostly node_modules, .next, archive)

---

## GitHub-Ready File Count
- Core Code: 12 files
- Configuration: 6 files  
- Documentation: 1 file
- Data: 3 files
- **Total: ~22 files** (vs 50+ now)
