# AI Content Agent System - Demo Script

## Quick Start

# Clone/enter project directory
cd ai-content-agent-system

# Start all services
docker-compose -f docker-compose.full.yml up -d

# Pull Gemma model (takes 2-5 minutes)
docker exec ai-agent-ollama ollama pull gemma:7b

# Wait for services to start, then access:
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
