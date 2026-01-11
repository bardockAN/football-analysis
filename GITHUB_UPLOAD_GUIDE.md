# 🚀 GitHub Upload Guide

## Step-by-Step Instructions to Upload to GitHub

### Step 1: Initialize Git Repository

```bash
cd D:\Footbal_analysis\football_analysis
git init
```

### Step 2: Add Files to Git

```bash
git add .
```

**What will be uploaded:**
- ✅ All Python source code (.py files)
- ✅ Configuration files (data.yaml, requirements.txt)
- ✅ Evaluation results (JSON, charts in evaluation_results/)
- ✅ Documentation (README.md, .md files)
- ✅ Directory structure (.gitkeep files)

**What will be IGNORED:**
- ❌ Model weights (.pt files) - Too large
- ❌ Videos (.mp4, .avi files) - Too large
- ❌ Dataset images (.jpg, .png) - Too large
- ❌ Training runs output
- ❌ __pycache__ and compiled Python files

### Step 3: Check What Will Be Committed

```bash
git status
```

You should see green files (to be committed) and no large files.

### Step 4: Make Initial Commit

```bash
git commit -m "Initial commit: Football Analysis System with YOLOv11"
```

### Step 5: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `football-analysis` (or your choice)
3. Description: "Football match analysis system using YOLOv11"
4. Choose: **Public** (recommended) or Private
5. **DO NOT** initialize with README (we already have one)
6. Click "Create repository"

### Step 6: Link to GitHub and Push

```bash
# Replace YOUR_USERNAME with your GitHub username
git remote add origin https://github.com/YOUR_USERNAME/football-analysis.git

# Rename branch to main (if needed)
git branch -M main

# Push to GitHub
git push -u origin main
```

### Step 7: Upload Model Weights Separately (Optional)

Since model weights are too large for GitHub, use GitHub Releases:

1. Go to your repository on GitHub
2. Click "Releases" → "Create a new release"
3. Tag: `v1.0.0`
4. Title: "Initial Release - YOLOv11 Model"
5. Upload `models/best.pt` file
6. Click "Publish release"

### Step 8: Add Sample Input Video Link (Optional)

Create a `input_videos/README.md`:

```markdown
# Input Videos

Due to file size limitations, videos are not included in this repository.

## Sample Video
Download a sample football match video and place it here:
- Place video as: `input_videos/your_video.mp4`
- Or download from: [Your Google Drive/Dropbox link]

## Supported Formats
- .mp4
- .avi
- .mov
```

## 📝 After Upload Checklist

- [ ] Repository is public/private as intended
- [ ] README.md displays correctly on GitHub
- [ ] No large files (>100MB) in repository
- [ ] .gitignore is working (check no .pt, .mp4, .avi files)
- [ ] Model weights uploaded to Releases
- [ ] Repository link added to your README badges
- [ ] Updated YOUR_USERNAME in README.md with actual username

## 🔄 Updating Repository Later

```bash
# After making changes
git add .
git commit -m "Description of changes"
git push
```

## ⚠️ Troubleshooting

### Error: File too large
```bash
# Remove large file from staging
git rm --cached path/to/large/file

# Add to .gitignore
echo "path/to/large/file" >> .gitignore

# Commit and push
git add .gitignore
git commit -m "Update gitignore"
git push
```

### Error: Authentication failed
```bash
# Use Personal Access Token instead of password
# Generate at: https://github.com/settings/tokens
# Use token as password when prompted
```

## 📦 Repository Size Estimate

After following this guide:
- **Total size**: ~50-100MB (without models/videos/dataset)
- **With model in Releases**: +200-500MB
- Safe for GitHub (free tier limit: 1GB per repo)

## 🎯 Next Steps

1. ✅ Add proper LICENSE file
2. ✅ Add shields.io badges to README
3. ✅ Create GitHub Actions for CI/CD (optional)
4. ✅ Add Issues/PR templates (optional)
5. ✅ Enable GitHub Pages for documentation (optional)

---

**Need help?** Open an issue on the repository or contact the maintainer.
