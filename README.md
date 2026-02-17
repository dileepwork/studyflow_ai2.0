# 🎓 StudyFlow AI - Lightweight Vercel Edition

**AI-Powered Study Planner** that analyzes syllabus PDFs and creates personalized study schedules.

## 🚀 What's New - Optimized for Vercel

### ✅ Deployment Size Reduced: 150MB → 20MB

**Key Changes:**
- 🔄 **Replaced spaCy** with Gemini API (saves ~60MB)
- ⚡ **Removed NetworkX** with custom graph algorithms (saves ~30MB)
- 🎯 **API-based AI** for better performance and zero model downloads
- 💰 **100% FREE** - No paid services required

---

## 🎯 Features

✅ **PDF Syllabus Analysis** - Upload syllabus, get topics extracted  
✅ **Dependency Detection** - Understands topic prerequisites  
✅ **Adaptive Scheduling** - Personalized study plans (Beginner/Intermediate/Advanced)  
✅ **AI Study Mentor** - Chat with AI for topic explanations  
✅ **Resource Links** - Auto-generated YouTube, GeeksforGeeks, notes  
✅ **Progress Tracking** - Mark topics as complete

---

## 📋 Quick Start

### 1️⃣ Get Gemini API Key (FREE)

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in and click **"Create API Key"**
3. Copy the key

### 2️⃣ Deploy to Vercel

**Option A: One-Click Deploy**

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/yourusername/studyflowai)

**Option B: Manual Deploy**

```powershell
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy
cd c:\Users\Dileep\studyflowai
vercel
```

### 3️⃣ Add API Key to Vercel

```powershell
vercel env add GEMINI_API_KEY
# Paste your API key
# Select all environments

# Redeploy
vercel --prod
```

**Or via Dashboard:**
1. Go to Vercel project → **Settings** → **Environment Variables**
2. Add `GEMINI_API_KEY` = `your_api_key`
3. Redeploy

### 4️⃣ Access Your App

Open: `https://your-project.vercel.app` 🎉

---

## 🛠️ Local Development

```powershell
# Clone repository
git clone <your-repo-url>
cd studyflowai

# Create .env file
echo "GEMINI_API_KEY=your_key_here" > .env

# Install Python dependencies
cd api
pip install -r requirements.txt

# Install Frontend dependencies
cd ../frontend
npm install

# Run backend (in one terminal)
cd ../api
python index.py

# Run frontend (in another terminal)
cd ../frontend
npm run dev
```

Visit: `http://localhost:5173` (frontend) + `http://localhost:5000` (backend)

---

## 📊 Tech Stack

### Frontend
- ⚛️ **React 19** - Modern UI framework
- 🎨 **Tailwind CSS** - Utility-first styling
- 🎬 **Framer Motion** - Smooth animations
- 📊 **Recharts** - Data visualization
- 🔥 **Firebase** - Authentication (optional)

### Backend (Serverless)
- 🐍 **Python + Flask** - API framework
- 🤖 **Google Gemini API** - AI-powered NLP
- 📄 **PyPDF** - PDF text extraction
- ⚡ **Vercel Serverless** - Zero-config deployment

---

## 🔄 How It Works

```mermaid
graph LR
    A[Upload PDF] --> B[Extract Text]
    B --> C[Gemini API - Extract Topics]
    C --> D[Analyze Dependencies]
    D --> E[Generate Schedule]
    E --> F[Display Dashboard]
    F --> G[AI Mentor Chat]
```

1. **Upload** syllabus PDF
2. **Extract** text using PyPDF
3. **AI Analysis** via Gemini API identifies topics
4. **Dependency Graph** shows learning prerequisites
5. **Adaptive Schedule** personalized to your level
6. **AI Chat** helps you understand concepts

---

## 📂 Project Structure

```
studyflowai/
├── api/
│   ├── index.py              # Flask serverless function
│   ├── utils.py              # PDF + Gemini NLP
│   ├── processor.py          # Scheduling algorithms
│   └── requirements.txt      # Lightweight Python deps
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── App.jsx          # Main app
│   │   └── main.jsx         # Entry point
│   ├── package.json
│   └── vite.config.js
├── vercel.json               # Deployment config
├── package.json              # Root build script
└── DEPLOYMENT_STEPS.md       # Detailed guide
```

---

## 💡 API Endpoints

### `GET /api/health`
Check if API is running

**Response:**
```json
{
  "status": "healthy",
  "message": "API is running!"
}
```

### `POST /api/analyze`
Analyze syllabus and generate schedule

**Request:**
- `file`: PDF file (multipart/form-data)
- `weeks`: Number of weeks (default: 4)
- `hours`: Hours per week (default: 10)
- `level`: Student level ("Beginner"/"Intermediate"/"Advanced")

**Response:**
```json
{
  "topics": ["Topic 1", "Topic 2", ...],
  "topic_details": {
    "Topic 1": {
      "difficulty": 1,
      "advice": "...",
      "resources": [...]
    }
  },
  "schedule": [...],
  "graph": {...}
}
```

### `POST /api/chat`
Chat with AI study mentor

**Request:**
```json
{
  "topic": "Neural Networks",
  "message": "What is backpropagation?"
}
```

**Response:**
```json
{
  "response": "Backpropagation is the learning engine..."
}
```

---

## 🎨 Customization

### Change AI Model
Edit `api/utils.py` and `api/processor.py`:
```python
# Switch to Gemini Pro for more advanced responses
gemini_model = genai.GenerativeModel('gemini-1.5-pro')
```

### Adjust Difficulty Weights
Edit `api/processor.py`:
```python
weights = {1: 2.5, 2: 3, 3: 4}  # Beginner weights
```

### Modify UI Theme
Edit `frontend/src/index.css` - Change color variables

---

## 🐛 Troubleshooting

### "GEMINI_API_KEY not set"
- Add environment variable to Vercel
- Redeploy after adding
- Check spelling: `GEMINI_API_KEY`

### Topics Not Extracting
- Check PDF text is readable (not scanned image)
- Verify API key is valid
- Check API quota (60 req/min limit)

### Build Fails
```powershell
# Test build locally
cd frontend
npm run build

# Check for errors
vercel logs
```

---

## 📈 Performance

- **Cold Start:** ~2-5 seconds (first request)
- **Warm Requests:** <500ms
- **PDF Analysis:** ~3-8 seconds (depends on PDF size)
- **AI Chat:** ~1-2 seconds

---

## 💰 Costs

**Total: $0/month** ✅

- ✅ Vercel Hobby: FREE (100GB bandwidth)
- ✅ Gemini API: FREE (60 req/min, 1500/day)
- ✅ No database costs

---

## 🔐 Security

- ✅ API keys stored as environment variables
- ✅ No data persistence (serverless)
- ✅ CORS enabled for frontend
- ✅ File uploads saved to `/tmp` (auto-deleted)

---

## 📄 License

MIT License - Feel free to use and modify!

---

## 🙏 Credits

Built with:
- [Google Gemini API](https://ai.google.dev/)
- [Vercel](https://vercel.com/)
- [React](https://react.dev/)
- [Flask](https://flask.palletsprojects.com/)

---

## 📞 Support

**Issues?** Check `DEPLOYMENT_STEPS.md` for detailed troubleshooting.

**Questions?** Open an issue on GitHub.

---

**🚀 Deployment Size: ~20MB (within 250MB limit) ✅**

Happy studying! 🎓
