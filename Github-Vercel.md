---
name: deploying-to-github-and-vercel
description: Automates pushing a local project to a new GitHub repository and deploying it as a new Vercel project. Use when the user asks to "push to GitHub", "deploy to Vercel", "put this on GitHub", "make this live", or "create a repo and deploy". Handles git initialization, GitHub repo creation, Vercel CLI deployment, and environment variable injection.
---

# Deploy to GitHub & Vercel

## When to use this skill
- User asks to push code to a new GitHub repo
- User asks to deploy a project to Vercel
- User asks to "make the site live" or "put it online"
- User wants both GitHub + Vercel set up in one flow

## Pre-flight Checklist
- [ ] Local project has all files ready
- [ ] `.gitignore` exists and excludes `.env*`, `node_modules/`, `dist/`
- [ ] `vercel.json` exists (create if missing — see below)
- [ ] GitHub token available in `mcp_config.json`
- [ ] Vercel token available (ask user if missing)
- [ ] Know all required env vars for the project (e.g. API keys)

---

## Workflow

### Step 1 — Initialize Git
```powershell
cd "PROJECT_DIR"
git init
git add README.md App.tsx index.html index.tsx package.json package-lock.json tsconfig.json vite.config.ts vercel.json
# Add any other project-specific files explicitly (avoid git add -A if .gitignore may be missing)
git config user.email "eyohannes1@users.noreply.github.com"
git config user.name "Eliab Yohannes"
git commit -m "Initial commit: [Project Name]"
```

> ⚠️ Do NOT `git add -A` before confirming `.gitignore` is in place — it will stage `node_modules`.

---

### Step 2 — Create GitHub Repo

The GitHub MCP token has **read/write** scope but **cannot create repos**. Use this exact flow:

#### Option A — User creates manually (default)
Tell the user:
> "Please go to **[github.com/new](https://github.com/new)**, create a repo named **`[REPO_NAME]`** with no README/gitignore/license checked, then say 'done'."

Wait for confirmation before Step 3.

#### Option B — GitHub CLI (if `gh` is installed)
```powershell
gh repo create [REPO_NAME] --public --description "[Description]" --source . --remote origin --push
```
Check first: `gh --version`

---

### Step 3 — Push to GitHub
```powershell
git remote add origin https://github.com/eyohannes1/[REPO_NAME].git
git branch -M main
git push -u origin main 2>&1
```

> ℹ️ Exit code 1 from PowerShell git push is normal — git writes to stderr. Verify success by checking for `main -> main` in output.

Verify push succeeded:
```powershell
# Use MCP tool: mcp_github-mcp-server_list_commits owner=eyohannes1 repo=[REPO_NAME] perPage=1
```

---

### Step 4 — Create `vercel.json`
If not already present, create at project root:
```json
{
  "framework": "vite",
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "installCommand": "npm install"
}
```
> Do NOT include `"name"` — it causes a deprecation warning in Vercel CLI v50+.

---

### Step 5 — Verify Vercel Token
```powershell
npx vercel whoami --token [VERCEL_TOKEN] 2>&1
```
- If output shows a username → ✅ proceed
- If "invalid token" → ask user to go to [vercel.com/account/tokens](https://vercel.com/account/tokens) and generate a new one

---

### Step 6 — Deploy to Vercel
```powershell
npx vercel deploy --token [VERCEL_TOKEN] --yes --prod 2>&1
```

Expected success output contains:
- `✅  Production: https://[project].vercel.app`
- `🔗  Aliased: https://[project].vercel.app`

---

### Step 7 — Add Environment Variables
For each required env var, run interactively:
```powershell
npx vercel env add [VAR_NAME] production --token [VERCEL_TOKEN] 2>&1
```
Respond to prompts:
- Sensitive? → `N` (unless it's a secret key)
- Value? → paste the value

Or use the Vercel MCP tool if available:
```
mcp_vercel_vercel_create_env_var projectId=[project-name] key=[VAR_NAME] value=[VALUE] target=["production","preview"]
```

---

### Step 8 — Redeploy to Apply Env Vars
```powershell
npx vercel deploy --token [VERCEL_TOKEN] --yes --prod 2>&1
```
Env vars only take effect after a fresh build.

---

### Step 9 — Commit `vercel.json` to GitHub
```powershell
git add vercel.json
git commit -m "Add Vercel configuration"
git push origin main 2>&1
```

---

## Known Gotchas
- **PowerShell exit code 1** from git is usually stderr output, not a real error — check the text output
- **Force pushing** to an existing repo will overwrite history — always confirm with user
- **Token scopes**: GitHub PAT in `mcp_config.json` cannot create or rename repos — user must do this manually
- **Vite env vars** must be prefixed `VITE_` to be exposed to the browser bundle
- **`vercel.json` name field** is deprecated in CLI v50+ — remove it to avoid warnings

## Resources
- Vercel token: [vercel.com/account/tokens](https://vercel.com/account/tokens)
- GitHub new repo: [github.com/new](https://github.com/new)
- See `scripts/deploy.ps1` for a one-shot automation script
