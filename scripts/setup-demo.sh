#!/bin/bash
# Setup demo script for AI Content Agent System

set -e

echo "🚀 Setting up AI Content Agent Demo..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Step 1/5: Starting Docker containers...${NC}"
docker-compose up -d

echo -e "${YELLOW}Step 2/5: Waiting for services to start...${NC}"
sleep 10

echo -e "${YELLOW}Step 3/5: Pulling Gemma 7B model (this may take a few minutes)...${NC}"
docker exec ai-agent-ollama ollama pull gemma:7b

echo -e "${YELLOW}Step 4/5: Initializing database...${NC}"
sleep 5

echo -e "${YELLOW}Step 5/5: Creating sample data...${NC}"

# Create sample brand voice
echo "Creating sample brand voice..."
curl -X POST "http://localhost:8000/api/v1/brand-voice" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Tech Startup",
    "description": "Modern tech company focused on AI",
    "config": {
      "tone": "professional yet approachable",
      "target_audience": "tech professionals and innovators",
      "key_topics": ["AI", "automation", "productivity", "innovation"],
      "avoid_topics": ["politics", "controversy"],
      "hashtag_strategy": "3-5 relevant hashtags",
      "cta_style": "question or value proposition",
      "formality_level": 7,
      "humor_allowed": true,
      "emoji_usage": {
        "linkedin": "minimal",
        "instagram": "moderate",
        "twitter": "moderate"
      },
      "banned_words": ["hate", "stupid", "failure"]
    }
  }' || echo "Brand voice creation skipped (might already exist)"

echo -e "${GREEN}✅ Demo setup complete!${NC}"
echo ""
echo -e "${YELLOW}📊 Access Information:${NC}"
echo "Backend API:      http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo "Ollama:           http://localhost:11434"
echo ""
echo -e "${YELLOW}🔐 Demo Credentials:${NC}"
echo "Admin:    admin@demo.com / demo123"
echo "Reviewer: reviewer@demo.com / demo123"
echo "Client:   client@demo.com / demo123"
echo ""
echo -e "${YELLOW}🚀 Quick Start:${NC}"
echo "1. Login as client@demo.com"
echo "2. Upload an image"
echo "3. Generate content for LinkedIn"
echo "4. Submit for approval"
echo "5. Login as reviewer@demo.com to approve"
echo "6. Login as admin@demo.com to control system"
echo ""
echo -e "${GREEN}Happy demoing! 🎉${NC}"
