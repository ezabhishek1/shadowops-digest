# ShadowOps Digest

[![CI/CD Pipeline](https://github.com/ezabhishek1/shadowops-digest/workflows/CI%2FCD%20Pipeline/badge.svg)](https://github.com/ezabhishek1/shadowops-digest/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![React 18.2](https://img.shields.io/badge/react-18.2-blue.svg)](https://reactjs.org/)

An AI-driven daily summary tool that clusters IT support tickets by root cause, generates actionable improvement suggestions, and estimates time/cost savings.

![ShadowOps Digest Demo](docs/demo-screenshot.png)

> **Note**: Replace the demo screenshot path with your actual screenshot once available.

## 🚀 New Here?

**Want to run this in 5 minutes?** Check out our [Quick Start Guide](QUICKSTART.md) for the fastest path to getting started!

## Features

- **AI-Powered Clustering**: Groups tickets by root cause using OpenAI embeddings or local ML algorithms
- **Smart Suggestions**: Generates actionable improvement recommendations based on ticket patterns
- **Cost Analysis**: Calculates time wasted and potential cost savings from implementing suggestions
- **Interactive Dashboard**: Clean React interface for inputting tickets and viewing results
- **Docker Ready**: Containerized setup for easy development and deployment

## Tech Stack

- **Backend**: FastAPI + Python 3.11
- **Frontend**: React.js + TailwindCSS
- **AI/ML**: OpenAI GPT-4, scikit-learn
- **Database**: PostgreSQL
- **Infrastructure**: Docker + Docker Compose

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.11+** - [Download here](https://www.python.org/downloads/)
- **Node.js 18+** - [Download here](https://nodejs.org/)
- **Git** - [Download here](https://git-scm.com/)
- **OpenAI API Key** - [Get one here](https://platform.openai.com/api-keys)
- **Docker** (Optional) - [Download here](https://www.docker.com/products/docker-desktop/)

### Verify Your Setup

Run our verification script to check if everything is ready:

**On Windows (PowerShell):**
```powershell
.\verify-setup.ps1
```

**On Mac/Linux:**
```bash
chmod +x verify-setup.sh
./verify-setup.sh
```

This will check all prerequisites and let you know if anything is missing.

## Quick Start (3 Options)

### Option 1: Docker (Recommended - Easiest)

Perfect if you have Docker installed. Everything runs in containers.

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/shadowops-digest.git
cd shadowops-digest

# 2. Create environment file
cp .env.example .env

# 3. Edit .env and add your OpenAI API key
# On Windows: notepad .env
# On Mac/Linux: nano .env
# Replace: OPENAI_API_KEY=your_openai_api_key_here

# 4. Start everything with Docker
docker-compose up --build

# Wait for services to start (about 2-3 minutes first time)
# You'll see: "Application startup complete" when ready
```

**Access the application:**
- 🌐 Frontend: http://localhost:3000
- 🔌 Backend API: http://localhost:8000
- 📚 API Docs: http://localhost:8000/docs

**To stop:**
```bash
# Press Ctrl+C, then:
docker-compose down
```

---

### Option 2: Local Development (Without Docker)

Run backend and frontend separately on your machine.

#### Step 1: Setup Backend

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file in backend directory
# Add: OPENAI_API_KEY=your_api_key_here

# Start backend server
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be running at: http://localhost:8000

#### Step 2: Setup Frontend (New Terminal)

```bash
# Navigate to frontend directory (from project root)
cd frontend

# Install dependencies
npm install

# Create .env file in frontend directory
# Add: REACT_APP_API_URL=http://localhost:8000

# Start frontend development server
npm start
```

Frontend will automatically open at: http://localhost:3000

---

### Option 3: Quick Test (Backend Only)

Just want to test the API without the UI?

```bash
# 1. Clone and navigate
git clone https://github.com/YOUR_USERNAME/shadowops-digest.git
cd shadowops-digest/backend

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set environment variable
# On Windows (PowerShell):
$env:OPENAI_API_KEY="your_api_key_here"
# On Windows (CMD):
set OPENAI_API_KEY=your_api_key_here
# On Mac/Linux:
export OPENAI_API_KEY="your_api_key_here"

# 4. Start server
python -m uvicorn main:app --reload

# 5. Test the API
# Visit: http://localhost:8000/docs
# Or use curl:
curl -X POST "http://localhost:8000/digest" \
  -H "Content-Type: application/json" \
  -d '{
    "tickets": ["VPN not connecting", "Password reset needed"],
    "avg_time_per_ticket_minutes": 30,
    "hourly_cost_usd": 40.0
  }'
```

---

## Verify Installation

After starting the application, verify everything works:

### 1. Check Backend Health
```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy"}
```

### 2. Check Frontend
Open http://localhost:3000 in your browser. You should see the ShadowOps Digest interface.

### 3. Test Full Workflow
1. Enter some sample tickets in the frontend
2. Click "Generate Digest"
3. View the clustered results and suggestions

---

## Development Workflow

### Running Tests

**Backend Tests:**
```bash
cd backend
pytest -v                          # Run all tests
pytest tests/test_clustering.py    # Run specific test file
pytest --cov=. --cov-report=html   # With coverage report
```

**Frontend Tests:**
```bash
cd frontend
npm test                    # Run tests in watch mode
npm test -- --coverage      # Run with coverage
npm test -- --watchAll=false  # Run once and exit
```

### Code Formatting

**Backend:**
```bash
cd backend
black .                    # Format Python code
flake8 .                   # Lint Python code
```

**Frontend:**
```bash
cd frontend
npm run format             # Format JavaScript (if configured)
npm run lint               # Lint JavaScript (if configured)
```

### Hot Reload

Both backend and frontend support hot reload:
- **Backend**: Changes to `.py` files automatically restart the server
- **Frontend**: Changes to `.jsx` files automatically refresh the browser

## Configuration

### Environment Variables

Create a `.env` file in the project root with these variables:

```bash
# Required - OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Optional - Database Configuration
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/shadowops_digest

# Optional - Application Configuration
ENVIRONMENT=development
LOG_LEVEL=INFO

# Optional - Frontend Configuration
REACT_APP_API_URL=http://localhost:8000
```

### Getting an OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in
3. Navigate to [API Keys](https://platform.openai.com/api-keys)
4. Click "Create new secret key"
5. Copy the key and add it to your `.env` file

**Note:** You'll need credits in your OpenAI account. The application uses:
- GPT-4 for suggestions (~$0.03 per request)
- Text embeddings for clustering (~$0.0001 per ticket)

### Configuration Options

**Backend (`backend/main.py`):**
- CORS origins (for production deployment)
- Clustering algorithm (OpenAI vs local ML)
- Logging level

**Frontend (`frontend/src/`):**
- API endpoint URL
- UI theme and styling
- Default form values

---

## API Usage

### POST /digest

**Request**:
```json
{
  "tickets": [
    "VPN not connecting on Windows 10",
    "Outlook password reset needed",
    "Printer not responding in Building A"
  ],
  "avg_time_per_ticket_minutes": 30,
  "hourly_cost_usd": 40.0
}
```

**Response**:
```json
{
  "clusters": {
    "Network Connectivity": [0],
    "Authentication Issues": [1],
    "Hardware Problems": [2]
  },
  "suggestion": "Create a VPN troubleshooting self-service guide",
  "time_wasted_hours": 1.5,
  "cost_saved_usd": 60.0,
  "digest_summary": "3 tickets clustered into 3 categories. Primary issue: Network Connectivity. Recommendation: VPN self-service guide. Potential savings: 1.5 hours, $60."
}
```

## Project Structure

```
shadowops-digest/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── models.py            # Pydantic data models
│   ├── clustering.py        # AI clustering logic
│   ├── suggestion.py        # Suggestion generation
│   ├── calculator.py        # Cost calculations
│   ├── summarizer.py        # Digest summarization
│   └── tests/               # Backend tests
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── hooks/           # Custom hooks
│   │   ├── pages/           # Page components
│   │   └── App.jsx          # Main app component
│   └── public/              # Static assets
├── docker-compose.yml       # Development environment
└── README.md               # This file
```

## Testing

### Backend Tests
```bash
cd backend
pytest -v
pytest --cov=. --cov-report=html  # with coverage report
```

### Frontend Tests
```bash
cd frontend
npm test
npm test -- --coverage  # with coverage report
```

## Troubleshooting

### Installation Issues

**Python not found:**
```bash
# Verify Python installation
python --version
# or
python3 --version

# If not installed, download from python.org
```

**Node/npm not found:**
```bash
# Verify Node installation
node --version
npm --version

# If not installed, download from nodejs.org
```

**pip install fails:**
```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Try installing with --user flag
pip install --user -r requirements.txt
```

**npm install fails:**
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and try again
rm -rf node_modules package-lock.json
npm install
```

### Runtime Issues

**Port already in use:**
```bash
# Check what's using the port
# On Windows:
netstat -ano | findstr :8000
netstat -ano | findstr :3000

# On Mac/Linux:
lsof -i :8000
lsof -i :3000

# Kill the process or use different ports:
# Backend:
uvicorn main:app --reload --port 8001

# Frontend:
PORT=3001 npm start
```

**Docker not starting:**
```bash
# Ensure Docker Desktop is running
docker --version

# Check port availability
docker-compose down -v

# Rebuild from scratch
docker-compose down -v
docker-compose build --no-cache
docker-compose up
```

**OpenAI API errors:**
```bash
# Verify API key is set
# On Windows (PowerShell):
echo $env:OPENAI_API_KEY

# On Mac/Linux:
echo $OPENAI_API_KEY

# Common issues:
# - API key is incorrect (check for typos)
# - No credits in OpenAI account
# - Rate limit exceeded
# - Network/firewall blocking OpenAI API
```

**Frontend can't connect to backend:**
```bash
# 1. Verify backend is running
curl http://localhost:8000/health

# 2. Check CORS settings in backend/main.py
# Should include: "http://localhost:3000"

# 3. Verify REACT_APP_API_URL in frontend/.env
# Should be: REACT_APP_API_URL=http://localhost:8000

# 4. Restart frontend after changing .env
cd frontend
npm start
```

**Module not found errors:**
```bash
# Backend:
cd backend
pip install -r requirements.txt

# Frontend:
cd frontend
npm install
```

**Database connection errors (if using PostgreSQL):**
```bash
# Check if PostgreSQL is running
docker-compose ps

# Reset database
docker-compose down -v
docker-compose up -d db
```

### Getting Help

If you're still stuck:

1. **Check the logs:**
   ```bash
   # Docker logs
   docker-compose logs backend
   docker-compose logs frontend
   
   # Local development logs
   # Check the terminal where you ran the commands
   ```

2. **Search existing issues:** [GitHub Issues](https://github.com/YOUR_USERNAME/shadowops-digest/issues)

3. **Create a new issue:** Include:
   - Your operating system
   - Python and Node versions
   - Full error message
   - Steps to reproduce

4. **Check documentation:**
   - [API Documentation](docs/API.md)
   - [Architecture Guide](docs/ARCHITECTURE.md)
   - [Deployment Guide](docs/DEPLOYMENT.md)

## Roadmap

- [ ] User authentication and multi-user support
- [ ] Integration with ticketing systems (Jira, ServiceNow)
- [ ] Historical analytics and trend analysis
- [ ] Export functionality (PDF, CSV)
- [ ] Scheduled digest generation
- [ ] Email notifications
- [ ] Custom clustering algorithm configuration

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details on:
- Setting up your development environment
- Code standards and best practices
- Testing requirements
- Pull request process

## Security

For security concerns, please review our [Security Policy](SECURITY.md) and report vulnerabilities responsibly.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a detailed history of changes.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- OpenAI for GPT-4 API
- FastAPI and React communities
- All contributors who help improve this project

## Support

- 📫 Issues: [GitHub Issues](https://github.com/ezabhishek1/shadowops-digest/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/ezabhishek1/shadowops-digest/discussions)
- 📖 Documentation: [Wiki](https://github.com/ezabhishek1/shadowops-digest/wiki)

---

## Quick Reference

### Common Commands

```bash
# Start everything (Docker)
docker-compose up

# Start backend only (local)
cd backend && python -m uvicorn main:app --reload

# Start frontend only (local)
cd frontend && npm start

# Run backend tests
cd backend && pytest

# Run frontend tests
cd frontend && npm test

# Check backend health
curl http://localhost:8000/health

# View API documentation
# Open: http://localhost:8000/docs

# Stop Docker services
docker-compose down

# Clean Docker volumes
docker-compose down -v
```

### Project URLs

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | Main application UI |
| Backend API | http://localhost:8000 | REST API endpoint |
| API Docs (Swagger) | http://localhost:8000/docs | Interactive API documentation |
| API Docs (ReDoc) | http://localhost:8000/redoc | Alternative API documentation |
| Health Check | http://localhost:8000/health | Service health status |

### File Structure Quick Reference

```
shadowops-digest/
├── .env                    # Environment variables (create from .env.example)
├── docker-compose.yml      # Docker configuration
├── backend/
│   ├── main.py            # API entry point
│   ├── requirements.txt   # Python dependencies
│   └── tests/             # Backend tests
└── frontend/
    ├── package.json       # Node dependencies
    ├── src/
    │   ├── App.jsx        # Main React component
    │   ├── components/    # Reusable components
    │   └── pages/         # Page components
    └── public/            # Static files
```

---

Made with ❤️ for IT teams everywhere