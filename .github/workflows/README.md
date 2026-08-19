# 🤖 HYDRA Blog Automation

This folder contains automated workflows that run on GitHub Actions.

## auto-post.yml

**What it does:** Every day at 9 AM (Brasilia time), an AI automatically writes and publishes a new blog post about the HYDRA ecosystem.

**How it works:**
1. GitHub wakes up the workflow automatically
2. Calls OpenRouter AI (using Gemini 2.0 Flash — free model)
3. AI writes a full blog post in JSON format
4. The file is saved to `src/data/posts/`
5. The blog updates on next deploy

**Manual trigger:**
You can run it manually anytime:
1. Go to your repo on GitHub
2. Click the **Actions** tab
3. Click **AI Auto Blog Post** on the left
4. Click **Run workflow** → **Run workflow**

**Required secret:**
- `OPENROUTER_API_KEY` — your OpenRouter API key (already configured)

**Post frequency:** Once per day (can be changed in the `cron` line)

**Model used:** `google/gemini-2.0-flash-exp:free` — completely free on OpenRouter
