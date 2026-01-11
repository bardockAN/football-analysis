# ⚡ Quick Upload Commands

Copy and paste these commands to upload to GitHub:

## 1️⃣ Initialize and Commit

```bash
cd D:\Footbal_analysis\football_analysis
git init
git add .
git commit -m "Initial commit: Football Analysis System with YOLOv11"
```

## 2️⃣ Create GitHub Repository

Go to: https://github.com/new
- Name: `football-analysis`
- Public repository
- DON'T initialize with README

## 3️⃣ Push to GitHub

**Replace YOUR_USERNAME with your actual GitHub username!**

```bash
git remote add origin https://github.com/YOUR_USERNAME/football-analysis.git
git branch -M main
git push -u origin main
```

## 4️⃣ Check Repository

Your repository should now be live at:
`https://github.com/YOUR_USERNAME/football-analysis`

## ✅ What Gets Uploaded

- ✅ All Python code
- ✅ README.md and documentation
- ✅ Evaluation results and charts
- ✅ Configuration files
- ✅ Project structure

## ❌ What Does NOT Get Uploaded (Too Large)

- ❌ Model weights (*.pt) - Upload to Releases separately
- ❌ Videos (*.mp4, *.avi)
- ❌ Dataset images (*.jpg, *.png)
- ❌ Training outputs (runs/)

## 🎯 Next: Upload Model Weights

1. Go to your repository on GitHub
2. Click "Releases" → "Create a new release"
3. Tag: `v1.0.0`
4. Upload `models/best.pt`
5. Publish release

---

**Done!** Your project is now on GitHub! 🎉
