# GitHub Repository Setup Guide

Follow these steps to push your project to GitHub and set it up properly.

## Step 1: Create GitHub Repository

1. Go to [GitHub](https://github.com) and log in
2. Click the "+" icon in the top right → "New repository"
3. Fill in the details:
   - **Repository name**: `shadowops-digest`
   - **Description**: "AI-driven IT support ticket analysis and digest generation tool"
   - **Visibility**: Choose Public or Private
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)
4. Click "Create repository"

## Step 2: Initialize Local Git Repository

```bash
cd shadowops-digest

# Initialize git (if not already done)
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: ShadowOps Digest v1.0.0"
```

## Step 3: Connect to GitHub

Replace `YOUR_USERNAME` with your actual GitHub username:

```bash
# Add remote
git remote add origin https://github.com/YOUR_USERNAME/shadowops-digest.git

# Verify remote
git remote -v

# Push to GitHub
git branch -M main
git push -u origin main
```

## Step 4: Configure Repository Settings

### Enable GitHub Actions

1. Go to your repository on GitHub
2. Click "Actions" tab
3. GitHub will automatically detect the workflow in `.github/workflows/ci.yml`
4. Enable Actions if prompted

### Add Repository Secrets

For CI/CD to work, add these secrets:

1. Go to Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add the following secrets:

| Secret Name | Description |
|-------------|-------------|
| `OPENAI_API_KEY` | Your OpenAI API key (for testing) |
| `CODECOV_TOKEN` | Codecov token (optional, for coverage reports) |

### Configure Branch Protection

1. Go to Settings → Branches
2. Click "Add rule"
3. Branch name pattern: `main`
4. Enable:
   - ✅ Require a pull request before merging
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging
   - ✅ Include administrators

### Enable Issues and Discussions

1. Go to Settings → General
2. Under "Features":
   - ✅ Enable Issues
   - ✅ Enable Discussions (optional, for community)
   - ✅ Enable Projects (optional, for project management)

## Step 5: Update README Badges

Edit `README.md` and replace `YOUR_USERNAME` with your GitHub username:

```markdown
[![CI/CD Pipeline](https://github.com/YOUR_USERNAME/shadowops-digest/workflows/CI%2FCD%20Pipeline/badge.svg)](https://github.com/YOUR_USERNAME/shadowops-digest/actions)
```

Commit and push the change:

```bash
git add README.md
git commit -m "Update README badges with correct username"
git push
```

## Step 6: Create Initial Release

1. Go to your repository on GitHub
2. Click "Releases" → "Create a new release"
3. Fill in:
   - **Tag version**: `v1.0.0`
   - **Release title**: `ShadowOps Digest v1.0.0`
   - **Description**: Copy from CHANGELOG.md
4. Click "Publish release"

## Step 7: Add Topics

1. Go to your repository homepage
2. Click the gear icon next to "About"
3. Add topics:
   - `ai`
   - `machine-learning`
   - `fastapi`
   - `react`
   - `it-support`
   - `ticket-analysis`
   - `python`
   - `javascript`
   - `docker`
4. Save changes

## Step 8: Create Project Board (Optional)

1. Go to "Projects" tab
2. Click "New project"
3. Choose "Board" template
4. Name it "ShadowOps Development"
5. Add columns:
   - Backlog
   - To Do
   - In Progress
   - Review
   - Done

## Step 9: Set Up GitHub Pages (Optional)

If you want to host documentation:

1. Go to Settings → Pages
2. Source: Deploy from a branch
3. Branch: `main`, folder: `/docs`
4. Save

## Step 10: Verify Everything Works

### Check CI/CD Pipeline

1. Go to "Actions" tab
2. Verify the workflow runs successfully
3. Fix any failing tests

### Test Clone and Setup

```bash
# Clone in a new directory
cd /tmp
git clone https://github.com/YOUR_USERNAME/shadowops-digest.git
cd shadowops-digest

# Verify setup works
cp .env.example .env
# Add your API key to .env
docker-compose up --build
```

## Additional Recommendations

### Add Collaborators

1. Go to Settings → Collaborators
2. Add team members with appropriate permissions

### Set Up Webhooks (Optional)

For Slack/Discord notifications:
1. Go to Settings → Webhooks
2. Add webhook URL
3. Select events to trigger notifications

### Enable Dependabot

1. Go to Settings → Security & analysis
2. Enable:
   - ✅ Dependabot alerts
   - ✅ Dependabot security updates
   - ✅ Dependabot version updates

### Create Wiki (Optional)

1. Go to "Wiki" tab
2. Create home page
3. Add documentation pages

## Maintenance Tasks

### Regular Updates

```bash
# Pull latest changes
git pull origin main

# Create feature branch
git checkout -b feature/new-feature

# Make changes, commit, push
git add .
git commit -m "Add new feature"
git push origin feature/new-feature

# Create pull request on GitHub
```

### Version Releases

```bash
# Update version in files
# Update CHANGELOG.md

# Commit changes
git add .
git commit -m "Bump version to v1.1.0"

# Create tag
git tag -a v1.1.0 -m "Release version 1.1.0"

# Push with tags
git push origin main --tags

# Create release on GitHub
```

## Troubleshooting

### Push Rejected

```bash
# Pull latest changes first
git pull origin main --rebase
git push origin main
```

### Large Files

If you accidentally committed large files:

```bash
# Remove from git history
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch path/to/large/file" \
  --prune-empty --tag-name-filter cat -- --all

# Force push
git push origin --force --all
```

### Reset to Remote

```bash
# Discard local changes
git fetch origin
git reset --hard origin/main
```

## Next Steps

1. ✅ Repository created and pushed
2. ✅ CI/CD pipeline configured
3. ✅ Documentation complete
4. ✅ Security policies in place
5. ✅ Contributing guidelines published

Your project is now ready for collaboration and deployment!

## Resources

- [GitHub Docs](https://docs.github.com)
- [GitHub Actions](https://docs.github.com/en/actions)
- [Semantic Versioning](https://semver.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)
