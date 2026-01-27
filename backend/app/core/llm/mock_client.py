"""
Mock LLM provider for demo and fallback.
"""
import asyncio
import random
import logging
from typing import Optional, Dict, Any
from datetime import datetime

from .provider import LLMProvider

logger = logging.getLogger(__name__)


class MockProvider(LLMProvider):
    """Mock LLM provider for demo and testing."""
    
    def __init__(self):
        self.responses = {
            "linkedin": [
                "Excited to share our latest insights on AI-powered automation! "
                "Our team has been exploring how intelligent agents can transform "
                "business workflows. What's your experience with AI automation? "
                "#AI #Automation #BusinessTransformation",
                
                "Just published: Key takeaways from our recent case study on "
                "content generation systems. The results show 3x faster content "
                "creation with human-in-the-loop approvals. "
                "#ContentCreation #CaseStudy #Productivity",
                
                "Industry shift alert: How AI-native development is changing "
                "the way we build software. No more traditional coding - just "
                "intelligent agents and workflows. Thoughts? "
                "#AINative #SoftwareDevelopment #Innovation"
            ],
            "instagram": [
                "✨ Something exciting is happening! Our AI agent just generated "
                "this amazing content. Swipe to see the before/after! "
                "#AI #ContentCreation #DigitalTransformation 📱💡",
                
                "Behind the scenes: Our content creation pipeline in action! "
                "From media upload to AI generation to human approval. "
                "#Tech #BehindTheScenes #Innovation 📸✨",
                
                "Just launched! Our new AI-powered content system is live. "
                "Tag someone who needs to see this! #Launch #AI #Tech"
            ],
            "twitter": [
                "AI-generated content with human approval? ✅\n"
                "Emergency controls and pause buttons? ✅\n"
                "Production-ready system demo? ✅\n"
                "\n"
                "Building the future of content creation. #AI #Dev #Tech",
                
                "Just automated our social media workflow with AI agents. "
                "Results: 10x faster content creation, 100% quality control. "
                "#Automation #Productivity #AI",
                
                "Question for my network: How are you using AI in your "
                "content creation process? #AIContent #Marketing #TechTalk"
            ]
        }
    
    async def generate_content(
        self, 
        prompt: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate mock content."""
        await asyncio.sleep(random.uniform(0.5, 1.5))  # Simulate processing
        
        platform = context.get("platform", "linkedin") if context else "linkedin"
        platform_responses = self.responses.get(platform, self.responses["linkedin"])
        
        content = random.choice(platform_responses)
        
        # Add context if provided
        if context and "media_description" in context:
            content = f"Inspired by: {context['media_description']}\n\n{content}"
        
        logger.info(f"Mock generated content for {platform}: {content[:100]}...")
        return content
    
    async def analyze_media(
        self, 
        image_path: str, 
        prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """Mock media analysis."""
        await asyncio.sleep(random.uniform(0.3, 0.8))
        
        return {
            "description": "A professional workspace with modern technology",
            "main_objects": ["computer", "desk", "monitor"],
            "colors": ["gray", "black"],
            "mood": "professional",
            "suggested_topics": ["remote work", "tech", "productivity"],
            "is_mock": True
        }
    
    async def is_available(self) -> bool:
        """Mock is always available."""
        return True
    
    def get_provider_name(self) -> str:
        return "mock"
