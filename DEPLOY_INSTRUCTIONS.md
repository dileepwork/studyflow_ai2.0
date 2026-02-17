# 🚀 How to Deploy StudyFlow AI on Vercel (Free)

You can deploy both the **Frontend** (React) and **Backend** (Python API) as a **single project** on Vercel for free.

## ✅ Prerequisites

1.  **GitHub Account**: You need to push this code to a GitHub repository.
2.  **Vercel Account**: Sign up at [vercel.com](https://vercel.com) using your GitHub account.
3.  **Gemini API Key**: You already have this in your `.env` file.

## 🛠️ Step 1: Prepare the Project (Already Done!)
I have updated `vercel.json` to ensure Vercel knows how to build your project.
-   It builds the frontend from the `frontend/` folder.
-   It serves the API from the `api/` folder.

## 📤 Step 2: Push to GitHub
1.  Create a new repository on GitHub (e.g., `studyflow-ai`).
2.  Open your terminal in this project folder and run:
    ```bash
    git init
    git add .
    git commit -m "Initial commit"
    git branch -M main
    git remote add origin https://github.com/YOUR_USERNAME/studyflow-ai.git
    git push -u origin main
    ```

## 🚀 Step 3: Deploy on Vercel
1.  Go to your [Vercel Dashboard](https://vercel.com/dashboard).
2.  Click **"Add New..."** -> **"Project"**.
3.  Import your `studyflow-ai` repository.
4.  **Configure Project**:
    *   **Framework Preset**: Select `Vite`.
    *   **Root Directory**: Leave it as `./` (Root).
    *   **Build Command**: Override and set to: `cd frontend && npm install && npm run build`
    *   **Output Directory**: Override and set to: `frontend/dist`
    *   **Install Command**: Override and set to: `cd frontend && npm install`
5.  **Environment Variables**:
    *   Expand the "Environment Variables" section.
    *   Add `GEMINI_API_KEY` with your key value (from `.env`).
    *   Add `VITE_API_URL` with value `/` (this points the frontend to the same domain's API).
6.  Click **Deploy**.

## 🎉 Success!
Once deployed, Vercel will give you a URL (e.g., `https://studyflow-ai.vercel.app`).
-   The frontend will load at `/`.
-   The API will align at `/api/...`.
