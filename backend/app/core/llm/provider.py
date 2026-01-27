"""
Abstract base class for LLM providers.
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import asyncio
import logging

logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    async def generate_content(
        self, 
        prompt: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate content from prompt and context."""
        pass
    
    @abstractmethod
    async def analyze_media(
        self, 
        image_path: str, 
        prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyze media file and return description."""
        pass
    
    @abstractmethod
    async def is_available(self) -> bool:
        """Check if provider is available."""
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Get provider name."""
        pass
