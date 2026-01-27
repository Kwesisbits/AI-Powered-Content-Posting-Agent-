"""
Ollama LLM provider implementation.
"""
import asyncio
import logging
from typing import Optional, Dict, Any
import httpx
from openai import AsyncOpenAI

from app.config import settings
from .provider import LLMProvider

logger = logging.getLogger(__name__)


class OllamaProvider(LLMProvider):
    """Ollama LLM provider using OpenAI-compatible API."""
    
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.LLM_MODEL
        self.timeout = settings.OLLAMA_TIMEOUT
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize OpenAI client for Ollama."""
        self.client = AsyncOpenAI(
            base_url=f"{self.base_url}/v1",
            api_key="ollama",  # Ollama doesn't check this
            timeout=self.timeout
        )
    
    async def generate_content(
        self, 
        prompt: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate content using Ollama."""
        try:
            # Build system message from context
            system_message = self._build_system_message(context)
            
            # Prepare messages
            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ]
            
            # Call Ollama
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            
            content = response.choices[0].message.content
            logger.info(f"Generated content with {self.model}: {content[:100]}...")
            return content
            
        except Exception as e:
            logger.error(f"Ollama generation failed: {str(e)}")
            raise
    
    async def analyze_media(
        self, 
        image_path: str, 
        prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze media file using vision capabilities.
        Note: Gemma 7B doesn't have vision, so we mock this.
        """
        # For demo, return mock analysis
        # In production, you'd use a vision model or CLIP
        
        mock_analysis = {
            "description": "A professional tech workspace with modern equipment",
            "main_objects": ["computer", "desk", "monitor", "coffee cup"],
            "colors": ["gray", "black", "white"],
            "mood": "professional, productive",
            "suggested_topics": ["remote work", "productivity", "tech setup"]
        }
        
        await asyncio.sleep(0.5)  # Simulate processing
        return mock_analysis
    
    async def is_available(self) -> bool:
        """Check if Ollama is available."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                return response.status_code == 200
        except Exception as e:
            logger.warning(f"Ollama not available: {str(e)}")
            return False
    
    def get_provider_name(self) -> str:
        return "ollama"
    
    def _build_system_message(self, context: Optional[Dict[str, Any]] = None) -> str:
        """Build system message from context."""
        system_message = "You are a professional social media content creator. "
        
        if context:
            if "brand_voice" in context:
                brand = context["brand_voice"]
                system_message += f"Write in this brand voice: {brand}. "
            
            if "platform" in context:
                platform = context["platform"]
                system_message += f"Create content for {platform}. "
                
                if platform == "linkedin":
                    system_message += "Use professional tone, focus on business value. "
                elif platform == "instagram":
                    system_message += "Use engaging, visual language. Include relevant emojis. "
                elif platform == "twitter":
                    system_message += "Be concise, use hashtags, engage with current trends. "
        
        system_message += "Respond only with the social media post content."
        return system_message
