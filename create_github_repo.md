# GitHub Repository Creation Instructions

## 🚀 Steps to Create GitHub Repository

### 1. Go to GitHub.com
- Open your browser and go to https://github.com
- Sign in to your account

### 2. Create New Repository
- Click the "+" icon in the top right corner
- Select "New repository"

### 3. Repository Settings
- **Repository name**: `uni-work`
- **Description**: `ASOA MITM Attack Demonstration - Automotive Security Research`
- **Visibility**: Public (or Private if you prefer)
- **DO NOT** initialize with README (we already have one)
- **DO NOT** add .gitignore (we already have one)
- **DO NOT** add license (optional)

### 4. Create Repository
- Click "Create repository"

### 5. Push Code from Pi
After creating the repository, run these commands on the Pi:

```bash
# Add the remote repository (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/uni-work.git

# Push the code
git branch -M main
git push -u origin main
```

### 6. Clone on Mac
On your Mac, run:
```bash
git clone https://github.com/YOUR_USERNAME/uni-work.git
cd uni-work
```

## 📁 What's Included

The repository contains:
- ✅ Complete ASOA framework
- ✅ Standalone sensor and dashboard applications
- ✅ MITM attack tools (both local and network)
- ✅ Setup scripts and documentation
- ✅ Working demonstration code

## 🎯 Next Steps

1. Create the GitHub repository using the steps above
2. Push the code from Pi
3. Clone on Mac
4. Follow the README.md instructions to run the demonstration

## 🔧 Alternative: Manual Upload

If you prefer, you can also:
1. Create the repository on GitHub
2. Download the files from the Pi using the web server
3. Upload them manually to GitHub

The web server is still running at: http://132.231.14.163:8000/
