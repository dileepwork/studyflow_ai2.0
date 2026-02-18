# Deploying to Vercel (Frontend + API)

This project is configured to deploy both the React frontend and Python API to Vercel in a single deployment.

## Prerequisites

1.  **Vercel Account**: Sign up at [vercel.com](https://vercel.com).
2.  **Node.js**: Ensure Node.js is installed.

## Option 1: Deploy using Vercel CLI (Recommended for quick test)

1.  **Install Vercel CLI**:
    Open your terminal in the project root (`c:\Users\dhine\Desktop\studyflow_ai2.0`) and run:
    ```bash
    npm install -g vercel
    ```

2.  **Login to Vercel**:
    ```bash
    vercel login
    ```
    Follow the prompts to authorize.

3.  **Deploy**:
    Run the deploy command:
    ```bash
    vercel
    ```

    - **Set up and deploy?**: `Y`
    - **Which scope?**: Select your account.
    - **Link to existing project?**: `N`
    - **Project Name**: `studyflow-ai` (or your choice)
    - **In which directory is your code located?**: `./` (Default)
    - **Auto-detected Project Settings**:
        - It might detect `Vite` or `Other`. Since we have a custom `vercel.json` and `api` folder, it should handle it.
        - If asked about build settings, you can usually accept defaults because `vercel.json` overrides them.
        - **IMPORTANT**: If it asks to override build command, say `N` (No), let it use the configuration.

4.  **Environment Variables**:
    After deployment starts or finishes, go to the Vercel Dashboard for your project.
    - Go to **Settings** > **Environment Variables**.
    - Add `GEMINI_API_KEY` with your API key value.
    - Redeploy if needed (or use `vercel --prod` to trigger a production build).

## Option 2: Deploy via GitHub (Recommended for production)

1.  Push your code to a GitHub repository.
2.  Go to Vercel Dashboard and click **"Add New..."** -> **"Project"**.
3.  Import your GitHub repository.
4.  Vercel should automatically detect the configuration from `vercel.json`.
5.  Add `GEMINI_API_KEY` in the Environment Variables section before clicking "Deploy".
6.  Click **Deploy**.

## Configuration Details (Already Set Up)

- **`vercel.json`**: Configures Vercel to build the frontend using React/Vite and serve the API using Python.
- **Frontend**: Builds to `frontend/dist`.
- **API**: Served from `api/index.py` at `/api/...`.

## Troubleshooting

- **404 on API calls**: Check if your axios calls use relative paths (e.g., `/api/chat`) and not `localhost:5000`.
- **Build Errors**: Check the Vercel logs. Ensure `frontend/dist` is created correctly.
