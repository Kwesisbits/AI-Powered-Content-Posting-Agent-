# AI-Powered-Content-Posting-Agent-



# 🤖 AI Content Agent System

A production-ready AI-powered content creation and social media posting platform with human-in-the-loop approvals, emergency controls, and local-first AI processing.

## 🚀 Features

### 🧠 **AI Content Generation**
- **Local LLM Integration**: Uses Ollama with Gemma 7B (no API costs)
- **Platform-Specific Templates**: LinkedIn, Instagram, Twitter/X
- **Brand Voice Enforcement**: Configurable tone, style, and guidelines
- **Media-Aware Generation**: Analyzes uploaded images/videos for context

### ⚡ **Workflow & Controls**
- **Approval-First Workflow**: No auto-publishing, strict human review
- **Instant Pause**: Halt all automation immediately
- **Manual-Only Mode**: AI generates drafts, manual approval required
- **Crisis Mode**: Emergency shutdown with content suppression
- **Role-Based Access Control**: Simulated permissions system

### 📱 **User Interface**
- **Media Upload Portal**: Drag-drop with preview
- **Approval Dashboard**: Visual workflow with accept/reject/edit
- **Control Panel**: Emergency controls with status indicators
- **Scheduling Calendar**: Visual post scheduling
- **Analytics Dashboard**: Mock engagement metrics

## 🏗️ Architecture


┌─────────────────────────────────────────────────┐
│               Frontend (Next.js)                │
│  • React 18 + TypeScript + Tailwind CSS        │
│  • shadcn/ui components                        │
│  • Real-time status updates                    │
└───────────────┬─────────────────────────────────┘
                │ HTTP/REST
┌───────────────▼─────────────────────────────────┐
│               Backend (FastAPI)                 │
│  • Python 3.11+                                │
│  • SQLAlchemy + SQLite/PostgreSQL              │
│  • JWT Authentication                          │
└───────────────┬─────────────────────────────────┘
                │
┌───────────────▼─────────────────────────────────┐
│                Core Services                    │
├─────────────────────────────────────────────────┤
│  • Content Agent (Ollama Gemma 7B)             │
│  • Approval Workflow Engine                     │
│  • Emergency Control System                     │
│  • Media Analysis & Processing                  │
└─────────────────────────────────────────────────┘


## 🛠️ Tech Stack

### **Backend**
- **Framework**: FastAPI (Python 3.11+)
- **Database**: SQLite (dev), PostgreSQL-ready
- **ORM**: SQLAlchemy 2.0 + Alembic migrations
- **AI/LLM**: Ollama + Gemma 7B (local, no API costs)
- **File Handling**: Python-multipart, aiofiles
- **Media Processing**: Pillow, OpenCV

### **Frontend**
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS + shadcn/ui
- **State Management**: React hooks + Context
- **HTTP Client**: Axios with interceptors

### **DevOps**
- **Containerization**: Docker + Docker Compose
- **Monitoring**: Health checks, structured logging
- **CI/CD**: GitHub Actions ready

## 📦 Quick Start

### Prerequisites
- Docker & Docker Compose
- 8GB+ RAM (for Ollama/Gemma)
- Git

### One-Command Setup
```bash
# Clone the repository
git clone https://github.com/yourusername/ai-content-agent-system.git
cd ai-content-agent-system

# Start all services (will pull Gemma 7B automatically)
./scripts/setup-demo.sh

# Or manually:
docker-compose up -d
```

### Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Ollama**: http://localhost:11434

## 🎯 Demo Credentials


Email: admin@demo.com
Password: demo123

Email: reviewer@demo.com  
Password: demo123

Email: client@demo.com
Password: demo123
```

## 🎬 Demo Script

### 1. **Media Upload & AI Generation** (0-3 min)
1. Login as `client@demo.com`
2. Upload sample image (`/samples/tech-office.jpg`)
3. Select "LinkedIn" platform
4. Generate AI content → Observe platform-specific adaptation

### 2. **Approval Workflow** (3-7 min)
1. Switch to `reviewer@demo.com`
2. Review pending drafts in dashboard
3. **Approve** one, **Request Changes** on another
4. Show edit history and version control

### 3. **Control Mechanisms** (7-10 min)
1. Login as `admin@demo.com`
2. Go to Control Panel
3. Click **"Instant Pause"** → Show all automation stops
4. Switch to **"Manual Mode"** → AI generates but requires manual steps
5. Activate **"Crisis Mode"** → Emergency shutdown with audit logs

### 4. **Scheduling & Posting** (10-12 min)
1. Schedule approved content
2. Show mock posting pipeline with realistic logs
3. Demonstrate analytics dashboard

### 5. **Architecture Walkthrough** (12-30 min)
- Show system design and trade-offs
- Explain local vs cloud AI strategy
- Demonstrate extensibility points

## 📁 Project Structure

```
ai-content-agent-system/
├── backend/                 # FastAPI application
│   ├── app/
│   │   ├── api/           # API routes and endpoints
│   │   ├── core/          # Business logic (agents, workflows, controls)
│   │   ├── models/        # SQLAlchemy models
│   │   ├── schemas/       # Pydantic schemas
│   │   └── services/      # Business services
│   ├── alembic/           # Database migrations
│   └── tests/             # Backend tests
├── frontend/              # Next.js application
│   ├── app/              # Next.js App Router
│   ├── components/       # React components
│   ├── lib/              # Utilities and hooks
│   └── types/            # TypeScript definitions
├── ollama-setup/         # Ollama configuration
├── scripts/              # Utility scripts
├── docs/                 # Documentation
└── docker/               # Docker configurations
```

## 🔧 Development Setup

### Local Development (Without Docker)
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Start Ollama separately
docker run -d -p 11434:11434 --name ollama ollama/ollama
docker exec ollama ollama pull gemma:7b

# Run backend
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

### Environment Variables
Create `.env` file:
```env
# Backend
DATABASE_URL=sqlite:///./content_agent.db
OLLAMA_BASE_URL=http://localhost:11434
LLM_PROVIDER=ollama
LLM_MODEL=gemma:7b
UPLOAD_DIR=./uploads
JWT_SECRET_KEY=your-secret-key-change-in-production

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

## 📊 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/media/upload` | Upload media files |
| POST | `/api/v1/content/generate` | Generate AI content |
| GET | `/api/v1/content/drafts` | List content drafts |
| POST | `/api/v1/approvals/{id}/approve` | Approve content |
| POST | `/api/v1/control/pause` | Pause automation |
| POST | `/api/v1/control/crisis-mode` | Emergency shutdown |
| GET | `/api/v1/analytics/posts` | Get posting analytics |

See full API documentation at http://localhost:8000/docs

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest tests/ -v

# Frontend tests
cd frontend
npm test

# E2E tests (requires running app)
npm run test:e2e
```

## 🐳 Docker Commands

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Rebuild specific service
docker-compose up -d --build backend

# Check service status
docker-compose ps

# Run database migrations
docker-compose exec backend alembic upgrade head

# Create sample data
docker-compose exec backend python scripts/create_sample_data.py
```

## 🔄 Workflow States

```
Draft → Pending Review → [Approve/Reject/Request Changes]
         ↓
   Approved → Scheduled → Published
         ↓
     Rejected → Archived
```

## 🚨 Emergency Controls

### **Instant Pause**
- Immediately halts all automated actions
- Queued posts remain in queue
- AI generation continues in manual mode

### **Manual-Only Mode**
- AI generates content but cannot auto-approve
- All posting requires explicit human action
- Scheduling is disabled

### **Crisis Mode**
- Emergency shutdown of all automation
- Cancels all scheduled posts
- Sends notifications to admins
- Requires manual reset to resume

## 📈 Production Deployment

### Railway (Recommended)
```bash
# Deploy with one click
railway up
```

### Docker Deployment
```bash
# Production build
docker-compose -f docker-compose.prod.yml up -d
```

### Environment Variables (Production)
```env
DATABASE_URL=postgresql://user:pass@host:5432/db
OLLAMA_BASE_URL=http://ollama:11434
REDIS_URL=redis://redis:6379
SENTRY_DSN=your-sentry-dsn
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Ollama** for providing easy local LLM serving
- **Google** for Gemma models
- **FastAPI** and **Next.js** teams for amazing frameworks


## 📞 Support

For issues and questions:
1. Check [Troubleshooting](docs/TROUBLESHOOTING.md)
2. Open a [GitHub Issue](https://github.com/Kwesisbits/Ai-Powered-Content-Posting-Agent-/issues)
3. Email: nanaamponsah391@gmail.com

---

