"""
LLM Provider factory and initialization.
"""
import logging
from typing import Optional
from app.config import settings
from .provider import LLMProvider
from .ollama_client import OllamaProvider
from .mock_client import MockProvider

logger = logging.getLogger(__name__)


class LLMProviderFactory:
    """Factory for creating LLM providers."""
    
    @staticmethod
    def create_provider(provider_name: Optional[str] = None) -> LLMProvider:
        """
        Create LLM provider based on configuration.
        
        Args:
            provider_name: Override provider name from config
            
        Returns:
            LLMProvider instance
        """
        provider_name = provider_name or settings.LLM_PROVIDER
        
        if provider_name == "ollama":
            provider = OllamaProvider()
            # Check if available, fallback to mock if not
            try:
                import asyncio
                available = asyncio.run(provider.is_available())
                if not available:
                    logger.warning("Ollama not available, falling back to mock")
                    provider = MockProvider()
            except Exception as e:
                logger.error(f"Error checking Ollama: {str(e)}")
                provider = MockProvider()
            
            return provider
        
        elif provider_name == "mock":
            return MockProvider()
        
        else:
            logger.warning(f"Unknown provider {provider_name}, using mock")
            return MockProvider()
    
    @staticmethod
    async def get_provider() -> LLMProvider:
        """Get provider with async availability check."""
        provider_name = settings.LLM_PROVIDER
        
        if provider_name == "ollama":
            provider = OllamaProvider()
            if await provider.is_available():
                return provider
            else:
                logger.warning("Ollama not available, using mock")
                return MockProvider()
        
        return MockProvider()


# Create singleton instance
llm_provider_factory = LLMProviderFactory()
