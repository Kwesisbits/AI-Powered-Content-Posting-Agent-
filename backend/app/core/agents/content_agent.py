"""
Main AI Content Agent - orchestrates content generation.
"""
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

from sqlalchemy.orm import Session

from app.config import settings
from app.core.llm import llm_provider_factory
from app.models import (
    ContentDraft, MediaAsset, BrandVoice, Platform, 
    ContentStatus, User
)
from app.schemas import ContentGenerationRequest

logger = logging.getLogger(__name__)


class ContentAgent:
    """Orchestrates AI-powered content generation."""
    
    def __init__(self, db: Session):
        self.db = db
        self.llm_provider = None
        self._initialize_llm_provider()
    
    def _initialize_llm_provider(self):
        """Initialize LLM provider."""
        self.llm_provider = llm_provider_factory.create_provider()
        logger.info(f"Content Agent using LLM provider: {self.llm_provider.get_provider_name()}")
    
    async def generate_content(
        self, 
        request: ContentGenerationRequest,
        user_id: int
    ) -> ContentDraft:
        """
        Generate content draft based on request.
        
        Args:
            request: Content generation request
            user_id: ID of user generating content
            
        Returns:
            Generated ContentDraft
        """
        # 1. Gather context
        context = await self._build_generation_context(request)
        
        # 2. Generate prompt
        prompt = self._build_generation_prompt(request, context)
        
        # 3. Generate content with LLM
        content_text = await self.llm_provider.generate_content(prompt, context)
        
        # 4. Extract hashtags (simple regex or let LLM handle)
        hashtags = self._extract_hashtags(content_text)
        
        # 5. Create and save content draft
        content_draft = ContentDraft(
            platform=request.platform,
            content_text=content_text,
            hashtags=json.dumps(hashtags) if hashtags else None,
            media_assets=json.dumps(request.media_asset_ids) if request.media_asset_ids else None,
            brand_voice_id=request.brand_voice_id,
            status=ContentStatus.DRAFT,
            generated_context=json.dumps(context),
            created_by=user_id,
            created_at=datetime.utcnow()
        )
        
        self.db.add(content_draft)
        self.db.commit()
        self.db.refresh(content_draft)
        
        logger.info(f"Generated content draft #{content_draft.id} for user #{user_id}")
        
        return content_draft
    
    async def _build_generation_context(
        self, 
        request: ContentGenerationRequest
    ) -> Dict[str, Any]:
        """Build context for content generation."""
        context = {
            "platform": request.platform.value,
            "generated_at": datetime.utcnow().isoformat()
        }
        
        # Add brand voice if specified
        if request.brand_voice_id:
            brand_voice = self.db.query(BrandVoice).filter(
                BrandVoice.id == request.brand_voice_id,
                BrandVoice.is_active == True
            ).first()
            
            if brand_voice:
                context["brand_voice"] = brand_voice.config
        
        # Add media analysis if media assets provided
        if request.media_asset_ids:
            media_context = await self._analyze_media_assets(request.media_asset_ids)
            context.update(media_context)
        
        # Add custom context if provided
        if request.context:
            context["user_context"] = request.context
        
        return context
    
    async def _analyze_media_assets(
        self, 
        media_asset_ids: List[int]
    ) -> Dict[str, Any]:
        """Analyze media assets and return context."""
        media_assets = self.db.query(MediaAsset).filter(
            MediaAsset.id.in_(media_asset_ids)
        ).all()
        
        if not media_assets:
            return {}
        
        # For demo, analyze first image
        media_asset = media_assets[0]
        
        try:
            analysis = await self.llm_provider.analyze_media(media_asset.filepath)
            return {
                "media_analysis": analysis,
                "has_media": True,
                "media_count": len(media_assets)
            }
        except Exception as e:
            logger.warning(f"Media analysis failed: {str(e)}")
            return {
                "media_analysis": {
                    "description": "Image included",
                    "main_objects": [],
                    "is_mock": True
                },
                "has_media": True,
                "media_count": len(media_assets)
            }
    
    def _build_generation_prompt(
        self, 
        request: ContentGenerationRequest,
        context: Dict[str, Any]
    ) -> str:
        """Build prompt for LLM based on request and context."""
        
        if request.prompt_override:
            return request.prompt_override
        
        platform = request.platform.value
        platform_prompts = {
            "linkedin": "Write a professional LinkedIn post about {topic}. Focus on business value and professional insights.",
            "instagram": "Create an engaging Instagram caption for {topic}. Make it visual and include relevant emojis.",
            "twitter": "Write a concise Twitter post about {topic}. Use hashtags and be engaging."
        }
        
        # Determine topic
        topic = "technology and AI"
        if "media_analysis" in context:
            media_desc = context["media_analysis"].get("description", "")
            topic = f"{media_desc} and technology"
        elif request.context:
            topic = request.context
        
        base_prompt = platform_prompts.get(platform, platform_prompts["linkedin"])
        prompt = base_prompt.format(topic=topic)
        
        # Add brand voice instructions
        if "brand_voice" in context:
            brand = context["brand_voice"]
            if isinstance(brand, dict):
                tone = brand.get("tone", "")
                audience = brand.get("target_audience", "")
                if tone:
                    prompt += f" Use a {tone} tone."
                if audience:
                    prompt += f" Target audience: {audience}."
        
        # Platform-specific instructions
        if platform == "twitter":
            prompt += " Keep it under 280 characters."
        elif platform == "instagram":
            prompt += " Make it visually descriptive."
        
        return prompt
    
    def _extract_hashtags(self, content: str) -> List[str]:
        """Extract hashtags from content."""
        import re
        hashtags = re.findall(r'#(\w+)', content)
        return list(set(hashtags))[:10]  # Max 10 unique hashtags
    
    async def regenerate_content(
        self, 
        draft_id: int,
        prompt_override: Optional[str] = None
    ) -> ContentDraft:
        """
        Regenerate content for an existing draft.
        
        Args:
            draft_id: ID of draft to regenerate
            prompt_override: Optional custom prompt
            
        Returns:
            New ContentDraft
        """
        # Get original draft
        original_draft = self.db.query(ContentDraft).filter(
            ContentDraft.id == draft_id
        ).first()
        
        if not original_draft:
            raise ValueError(f"Draft #{draft_id} not found")
        
        # Create new draft based on original
        new_draft = ContentDraft(
            platform=original_draft.platform,
            content_text="",  # Will be generated
            hashtags=original_draft.hashtags,
            media_assets=original_draft.media_assets,
            brand_voice_id=original_draft.brand_voice_id,
            status=ContentStatus.DRAFT,
            generated_context=original_draft.generated_context,
            created_by=original_draft.created_by,
            created_at=datetime.utcnow()
        )
        
        # Prepare request
        request = ContentGenerationRequest(
            platform=original_draft.platform,
            media_asset_ids=json.loads(original_draft.media_assets) if original_draft.media_assets else None,
            brand_voice_id=original_draft.brand_voice_id,
            context="Regenerate with improvements",
            prompt_override=prompt_override
        )
        
        # Generate new content
        context = await self._build_generation_context(request)
        prompt = prompt_override or self._build_generation_prompt(request, context)
        new_content = await self.llm_provider.generate_content(prompt, context)
        
        # Update new draft
        new_draft.content_text = new_content
        
        self.db.add(new_draft)
        self.db.commit()
        self.db.refresh(new_draft)
        
        logger.info(f"Regenerated content from draft #{draft_id} as draft #{new_draft.id}")
        
        return new_draft
