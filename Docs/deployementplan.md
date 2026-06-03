# Deployment Plan: Mutual Fund FAQ Assistant

This document outlines the step-by-step process for deploying the decoupled architecture of the Mutual Fund FAQ Assistant to production.

## 1. Version Control Setup
Before deploying, ensure your entire codebase is pushed to a Git repository (e.g., GitHub, GitLab, or Bitbucket). Both Railway and Vercel will connect directly to this repository to automate future deployments.

## 2. Backend Deployment (Railway)
The backend is a FastAPI application that handles database querying, compliance verification, and LLM orchestration. 

### Steps:
1. **Create Project:** Log into [Railway.app](https://railway.app/) and create a new project by clicking **"Deploy from GitHub repo"**.
2. **Select Repository:** Choose the Mutual Fund repository.
3. **Environment Variables:** Before clicking deploy, go to the **Variables** tab and add your API key:
   - `GEMINI_API_KEY` = `your_gemini_2.5_flash_api_key_here`
4. **Configuration:** 
   - Railway will automatically detect the `Procfile` at the root of the project.
   - It will execute the startup command: `uvicorn src.api:app --host 0.0.0.0 --port $PORT`.
5. **Deploy & Get URL:** Click Deploy. Once finished, go to the **Settings** tab and generate a public domain (e.g., `https://your-backend-app.up.railway.app`). **Copy this URL.**

> [!IMPORTANT]
> Keep this backend URL handy, as you will need to inject it into the frontend application.

---

## 3. Frontend Deployment (Vercel)
The frontend is a static HTML/CSS/JS application that communicates with the backend via REST API.

### Steps:
1. **Update API Endpoint:** Open your local codebase and go to `frontend/app.js`. Change the placeholder URL on line 4 to the Railway URL you copied in the previous step:
   ```javascript
   const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
       ? 'http://127.0.0.1:8000' 
       : 'https://your-actual-railway-url.up.railway.app';
   ```
2. **Commit Changes:** Commit and push this change to your GitHub repository.
3. **Create Project:** Log into [Vercel](https://vercel.com/) and click **"Add New Project"**.
4. **Select Repository:** Import your Mutual Fund repository.
5. **Configuration:**
   - **Framework Preset:** Leave as `Other`.
   - **Root Directory:** Click "Edit" and select `frontend` from the dropdown list.
   - Vercel will automatically detect `vercel.json` for routing rules.
6. **Deploy:** Click Deploy. Your interactive web assistant will now be live on a public URL!

---

## 4. Daily Database Synchronization (GitHub Actions)
To ensure the facts served by the RAG system are never stale, a GitHub action will automate the Groww scraping daily.

### Steps:
1. Verify the `.github/workflows/daily_sync.yml` file is present in your repository.
2. Go to your GitHub repository in the web browser.
3. Navigate to **Settings > Secrets and variables > Actions**.
4. (Optional) If your scraper relies on any API keys, add them here. Currently, `src/sync.py` only relies on public web scraping and local ChromaDB ingestion, so no secrets are strictly necessary for the sync job itself.
5. The workflow is scheduled to run daily at `00:00 UTC`. It will scrape Groww, update `data/schemes.json`, and commit the updated `db/` back to the repository so Railway pulls the latest data on its next deploy.

> [!NOTE]
> If the GitHub action detects a change and commits to the `main` branch, Railway and Vercel will both automatically trigger a redeploy, meaning your production application will update completely hands-free!
