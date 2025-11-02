# Quick Start Guide

Get ShadowOps Digest running in 5 minutes or less!

## Prerequisites Check

Before starting, verify you have these installed:

```bash
# Check Python (need 3.11+)
python --version

# Check Node.js (need 18+)
node --version

# Check Git
git --version
```

Don't have them? Quick install:
- **Python**: https://www.python.org/downloads/
- **Node.js**: https://nodejs.org/
- **Git**: https://git-scm.com/

## 🚀 Fastest Path: Docker

**Have Docker?** This is the easiest way:

```bash
# 1. Clone
git clone https://github.com/YOUR_USERNAME/shadowops-digest.git
cd shadowops-digest

# 2. Setup environment
cp .env.example .env

# 3. Add your OpenAI API key to .env
# Windows: notepad .env
# Mac/Linux: nano .env

# 4. Start everything
docker-compose up --build
```

**Done!** Open http://localhost:3000

---

## 🏃 Fast Path: Local Development

**No Docker?** Run locally:

### Terminal 1 - Backend

```bash
# Clone and navigate
git clone https://github.com/YOUR_USERNAME/shadowops-digest.git
cd shadowops-digest/backend

# Install dependencies
pip install -r requirements.txt

# Set API key (replace with your actual key)
# Windows PowerShell:
$env:OPENAI_API_KEY="sk-your-key-here"
# Mac/Linux:
export OPENAI_API_KEY="sk-your-key-here"

# Start backend
python -m uvicorn main:app --reload
```

### Terminal 2 - Frontend

```bash
# Navigate to frontend (from project root)
cd shadowops-digest/frontend

# Install dependencies
npm install

# Start frontend
npm start
```

**Done!** Browser opens automatically at http://localhost:3000

---

## ✅ Verify It Works

1. **Check backend health:**
   ```bash
   curl http://localhost:8000/health
   ```
   Should return: `{"status":"healthy"}`

2. **Open frontend:**
   Go to http://localhost:3000

3. **Test the app:**
   - Enter some sample tickets:
     - "VPN not connecting"
     - "Password reset needed"
     - "Printer offline"
   - Set time: 30 minutes
   - Set cost: $40/hour
   - Click "Generate Digest"
   - See the magic! ✨

---

## 🆘 Quick Troubleshooting

### "Port already in use"

**Backend (port 8000):**
```bash
# Use different port
python -m uvicorn main:app --reload --port 8001
```

**Frontend (port 3000):**
```bash
# Use different port
PORT=3001 npm start
```

### "OpenAI API error"

- Check your API key is correct
- Verify you have credits: https://platform.openai.com/account/usage
- Make sure key starts with `sk-`

### "Module not found"

**Backend:**
```bash
cd backend
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
```

### "Can't connect to backend"

1. Make sure backend is running (check Terminal 1)
2. Verify it's on port 8000: http://localhost:8000/health
3. Restart frontend if you changed .env

---

## 🎯 Next Steps

Now that it's running:

1. **Explore the API docs:** http://localhost:8000/docs
2. **Read the full README:** [README.md](README.md)
3. **Check the architecture:** [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
4. **Run the tests:**
   ```bash
   cd backend && pytest
   cd frontend && npm test
   ```

---

## 📝 Sample Test Data

Try these tickets to see clustering in action:

**Network Issues:**
- "VPN connection keeps dropping"
- "Can't access shared drive"
- "WiFi not working in conference room"

**Authentication:**
- "Password reset needed"
- "Account locked out"
- "Can't login to email"

**Hardware:**
- "Printer not responding"
- "Monitor flickering"
- "Keyboard keys not working"

**Software:**
- "Outlook keeps crashing"
- "Excel file won't open"
- "Teams video not working"

---

## 🛑 Stopping the Application

**Docker:**
```bash
# Press Ctrl+C, then:
docker-compose down
```

**Local:**
```bash
# Press Ctrl+C in both terminals
```

---

## 💡 Pro Tips

1. **Save your API key:** Add it to `.env` file so you don't have to set it every time
2. **Use Docker:** It's easier and handles all dependencies
3. **Check logs:** If something breaks, the terminal shows helpful error messages
4. **Start small:** Test with 3-5 tickets first, then scale up

---

## 🎉 You're All Set!

Questions? Check the [full documentation](README.md) or [open an issue](https://github.com/YOUR_USERNAME/shadowops-digest/issues).

Happy clustering! 🚀
