# **README.md**

## **AI-Powered Content & Posting Agent System**

A production-ready AI-native content creation platform with human-in-the-loop approvals, emergency controls, and platform-specific content generation.

### **Key Features**

#### **AI Content Generation**
- Platform-specific templates (LinkedIn, Instagram, Twitter)
- Brand voice configuration and enforcement
- Media-aware content creation from uploaded assets
- Provider-agnostic architecture (Ollama, OpenAI, or Mock)

#### **Approval-First Workflow**
- No auto-publishing - all content requires human approval
- Multi-role system (Client, Reviewer, Admin)
- Complete audit trail and version history
- State machine for content lifecycle management

#### **Emergency Control Systems**
- **Instant Pause**: Immediate halt of all automation
- **Manual-Only Mode**: AI generates but requires manual approval
- **Crisis Mode**: Emergency shutdown with content suppression
- System-wide status dashboard with real-time monitoring

#### **Platform Integration**
- Mock social media posting pipeline
- Scheduling system with calendar integration
- Analytics dashboard with engagement metrics
- Media upload with preview and analysis

### **System Architecture**

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Frontend      │────▶│    Backend      │────▶│   AI Provider   │
│   (Next.js)     │     │   (FastAPI)     │     │  (Ollama/Mock)  │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                       │                       │
         │                       │                       │
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Approval      │     │   Control       │     │   Database      │
│   Workflow      │     │   System        │     │   (SQLite)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

### **Quick Start**

#### **1. Backend Setup**
```bash
cd backend
python -m venv venv

# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt

# For mock mode (no Ollama required):
echo "LLM_PROVIDER=mock" > .env

# For Ollama mode:
echo "LLM_PROVIDER=ollama" > .env
echo "OLLAMA_BASE_URL=http://localhost:11434" >> .env

python run.py
```

#### **2. Frontend Setup**
```bash
cd frontend
npm install
npm run dev
```

#### **3. Access the Application**
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### **Demo Credentials**

- **Admin**: `admin@demo.com` / `demo123`
  - Full system access including emergency controls
- **Reviewer**: `reviewer@demo.com` / `demo123`
  - Content approval and review capabilities
- **Client**: `client@demo.com` / `demo123`
  - Content creation and submission

### **Demo Script (15 Minutes)**

#### **Part 1: Content Creation (3 min)**
1. Login as `client@demo.com`
2. Upload sample media (image/video)
3. Generate platform-specific content
4. Submit for approval

#### **Part 2: Approval Workflow (3 min)**
1. Login as `reviewer@demo.com`
2. Review pending content in dashboard
3. Approve one item, request changes on another
4. Show version history and audit trail

#### **Part 3: Emergency Controls (3 min)**
1. Login as `admin@demo.com`
2. Navigate to Control Panel
3. Demonstrate "Instant Pause" functionality
4. Switch to "Manual Mode" and "Crisis Mode"
5. Show system status monitoring

#### **Part 4: System Features (3 min)**
1. Show media library and upload functionality
2. Demonstrate scheduling system
3. Display analytics dashboard
4. Review API documentation

#### **Part 5: Architecture Walkthrough (3 min)**
1. Explain provider-agnostic AI integration
2. Show approval state machine design
3. Discuss control system implementation
4. Review production readiness features

### **Technical Architecture**

#### **Backend (FastAPI)**
- **Framework**: FastAPI with Python 3.11+
- **Database**: SQLite (production-ready for PostgreSQL)
- **AI Integration**: Provider-agnostic with Ollama/Mock/OpenAI support
- **Authentication**: JWT-based with role management
- **File Handling**: Local storage with S3-ready abstraction

#### **Frontend (Next.js)**
- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS with shadcn/ui components
- **State Management**: React Query + Context API
- **Build**: Static generation with API routes

#### **AI/LLM Integration**
- **Primary**: Ollama with Gemma 7B (local, no API costs)
- **Fallback**: Mock provider for reliability
- **Extensible**: OpenAI/Anthropic API ready
- **Context Management**: Brand voice and platform awareness

### **Production Readiness Features**

#### **Monitoring & Observability**
- Health check endpoints
- Structured JSON logging
- Performance metrics collection
- Error tracking and alerting

#### **Security & Controls**
- Role-based access control
- Audit logging for all actions
- Input validation and sanitization
- Rate limiting and request throttling

#### **Scalability & Maintenance**
- Database migrations with Alembic
- Configuration via environment variables
- Containerized deployment ready
- Horizontal scaling support

### **Evaluation Criteria Coverage**

#### **AI-Native Thinking**
- Agent orchestration vs monolithic LLM calls
- State management across workflow steps
- Context preservation and optimization
- Fallback strategies and error handling

#### **Practical System Design**
- Separation of concerns and modular architecture
- Database schema design with relationships
- API design with proper versioning
- File handling and storage abstraction

#### **Production Readiness Mindset**
- Emergency controls and safety mechanisms
- Monitoring and alerting implementation
- Configuration management
- Deployment and maintenance considerations

#### **Clarity of Communication**
- Comprehensive API documentation
- Clear code structure and comments
- Architecture documentation
- Deployment and setup instructions

### **Project Structure**

```
ai-content-agent-system/
├── backend/
│   ├── app/
│   │   ├── api/              # API endpoints and routing
│   │   ├── core/             # Business logic (agents, workflows, controls)
│   │   ├── models/           # Database models
│   │   ├── schemas/          # Pydantic schemas
│   │   └── services/         # Business services
│   ├── tests/               # Backend tests
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── app/                 # Next.js App Router
│   ├── components/          # React components
│   ├── lib/                 # Utilities and hooks
│   ├── types/               # TypeScript definitions
│   └── public/              # Static assets
├── docker-compose.yml       # Multi-container setup
└── README.md               # This file
```

### **Deployment Options**

#### **Local Development**
- Python virtual environment + Node.js
- SQLite database (no external dependencies)
- Mock AI provider for zero-cost testing

#### **Docker Deployment**
- Multi-container setup with Ollama
- Production-ready configuration
- Environment-based customization

#### **Cloud Deployment**
- Backend: Railway, Render, or AWS
- Frontend: Vercel or Netlify
- Database: PostgreSQL or AWS RDS

### **Development Setup**

1. Clone the repository
2. Setup backend with `pip install -r requirements.txt`
3. Setup frontend with `npm install`
4. Configure environment variables
5. Initialize database with `python -c "from app.database import init_db; init_db()"`
6. Start services with `python run.py` and `npm run dev`

### **Testing**

```bash
# Backend tests
cd backend
pytest tests/ -v

# API testing
curl http://localhost:8000/health
curl http://localhost:8000/docs

# Full system test
python test_backend.py
```

### **License**

MIT License - see LICENSE file for details.

### **Contact**

For questions or issues, please open an issue on the GitHub repository.

---

**Built for the Native AI Engineer role case study assessment.**
