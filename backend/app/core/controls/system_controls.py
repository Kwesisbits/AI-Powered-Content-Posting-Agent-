"""
System-wide control mechanisms for emergency scenarios.
"""
import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum
from sqlalchemy.orm import Session

from app.models import SystemStatus, SystemMode, User, AuditLog
from app.schemas import SystemMode as SchemaSystemMode

logger = logging.getLogger(__name__)


class ControlAction(str, Enum):
    PAUSE = "pause"
    RESUME = "resume"
    SET_MANUAL = "set_manual"
    SET_CRISIS = "set_crisis"
    SET_NORMAL = "set_normal"


class SystemControls:
    """
    Centralized control system for emergency scenarios.
    
    Manages:
    - Instant Pause: Halt all automation
    - Manual Mode: AI generates but manual approval/posting required
    - Crisis Mode: Emergency shutdown
    """
    
    def __init__(self, db: Optional[Session] = None):
        self.db = db
        self.current_mode: SystemMode = SystemMode.NORMAL
        self.is_paused: bool = False
        self._lock = asyncio.Lock()
        self._last_update: Optional[datetime] = None
        
        # Callbacks for subsystems to register
        self._pause_callbacks = []
        self._mode_change_callbacks = []
    
    async def initialize(self, db: Optional[Session] = None):
        """Initialize system controls from database."""
        if db:
            self.db = db
        
        if self.db:
            # Load current status from database
            system_status = self.db.query(SystemStatus).first()
            if system_status:
                self.current_mode = system_status.mode
                self.is_paused = system_status.is_paused
                self._last_update = system_status.last_updated_at
            else:
                # Create initial status
                system_status = SystemStatus(
                    mode=self.current_mode,
                    is_paused=self.is_paused,
                    last_updated_at=datetime.utcnow()
                )
                self.db.add(system_status)
                self.db.commit()
        
        logger.info(
            f"System controls initialized: mode={self.current_mode}, "
            f"paused={self.is_paused}"
        )
    
    async def execute_action(
        self, 
        action: ControlAction,
        user_id: Optional[int] = None,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute control action.
        
        Args:
            action: Control action to execute
            user_id: User ID executing the action
            notes: Optional notes about the action
            
        Returns:
            Dictionary with action result and new state
        """
        async with self._lock:
            previous_mode = self.current_mode
            previous_paused = self.is_paused
            
            try:
                if action == ControlAction.PAUSE:
                    await self._pause_system(user_id, notes)
                elif action == ControlAction.RESUME:
                    await self._resume_system(user_id, notes)
                elif action == ControlAction.SET_MANUAL:
                    await self._set_manual_mode(user_id, notes)
                elif action == ControlAction.SET_CRISIS:
                    await self._set_crisis_mode(user_id, notes)
                elif action == ControlAction.SET_NORMAL:
                    await self._set_normal_mode(user_id, notes)
                else:
                    raise ValueError(f"Unknown action: {action}")
                
                # Update database if available
                if self.db:
                    await self._update_database_status(user_id, notes)
                
                # Log audit
                await self._log_audit(action, user_id, {
                    "previous_mode": previous_mode.value,
                    "previous_paused": previous_paused,
                    "new_mode": self.current_mode.value,
                    "new_paused": self.is_paused,
                    "notes": notes
                })
                
                logger.info(
                    f"Control action '{action}' executed by user #{user_id}. "
                    f"Mode: {previous_mode} -> {self.current_mode}, "
                    f"Paused: {previous_paused} -> {self.is_paused}"
                )
                
                return {
                    "success": True,
                    "action": action,
                    "previous_mode": previous_mode.value,
                    "previous_paused": previous_paused,
                    "current_mode": self.current_mode.value,
                    "current_paused": self.is_paused,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
            except Exception as e:
                logger.error(f"Failed to execute control action '{action}': {str(e)}")
                raise
    
    async def _pause_system(self, user_id: Optional[int], notes: Optional[str]):
        """Pause all automation immediately."""
        self.is_paused = True
        await self._execute_pause_callbacks()
    
    async def _resume_system(self, user_id: Optional[int], notes: Optional[str]):
        """Resume automation."""
        self.is_paused = False
    
    async def _set_manual_mode(self, user_id: Optional[int], notes: Optional[str]):
        """Set system to manual mode."""
        self.current_mode = SystemMode.MANUAL
        self.is_paused = False  # Manual mode doesn't mean paused
    
    async def _set_crisis_mode(self, user_id: Optional[int], notes: Optional[str]):
        """Set system to crisis mode (emergency shutdown)."""
        self.current_mode = SystemMode.CRISIS
        self.is_paused = True  # Crisis mode always paused
        
        # Execute emergency callbacks
        await self._execute_pause_callbacks()
        await self._execute_crisis_callbacks()
    
    async def _set_normal_mode(self, user_id: Optional[int], notes: Optional[str]):
        """Set system to normal mode."""
        self.current_mode = SystemMode.NORMAL
        self.is_paused = False
    
    async def _update_database_status(
        self, 
        user_id: Optional[int], 
        notes: Optional[str]
    ):
        """Update system status in database."""
        system_status = self.db.query(SystemStatus).first()
        if not system_status:
            system_status = SystemStatus()
            self.db.add(system_status)
        
        system_status.mode = self.current_mode
        system_status.is_paused = self.is_paused
        system_status.last_updated_by = user_id
        system_status.last_updated_at = datetime.utcnow()
        system_status.notes = notes
        
        self.db.commit()
    
    async def _log_audit(
        self, 
        action: ControlAction,
        user_id: Optional[int],
        details: Dict[str, Any]
    ):
        """Log control action to audit log."""
        if self.db and user_id:
            audit_log = AuditLog(
                user_id=user_id,
                action=f"control_{action}",
                entity_type="system",
                entity_id=None,
                details=details,
                timestamp=datetime.utcnow()
            )
            self.db.add(audit_log)
            self.db.commit()
    
    async def _execute_pause_callbacks(self):
        """Execute registered pause callbacks."""
        for callback in self._pause_callbacks:
            try:
                await callback(self.is_paused)
            except Exception as e:
                logger.error(f"Pause callback failed: {str(e)}")
    
    async def _execute_crisis_callbacks(self):
        """Execute registered crisis callbacks."""
        # In production, this would notify admins, cancel scheduled posts, etc.
        logger.warning("CRISIS MODE ACTIVATED - Emergency shutdown procedures initiated")
    
    def register_pause_callback(self, callback):
        """Register callback for pause/resume events."""
        self._pause_callbacks.append(callback)
    
    def register_mode_change_callback(self, callback):
        """Register callback for mode change events."""
        self._mode_change_callbacks.append(callback)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current system status."""
        return {
            "mode": self.current_mode.value,
            "is_paused": self.is_paused,
            "last_updated": self._last_update.isoformat() if self._last_update else None,
            "can_auto_approve": self.can_auto_approve(),
            "can_auto_post": self.can_auto_post(),
            "can_generate_content": self.can_generate_content()
        }
    
    def can_auto_approve(self) -> bool:
        """Check if system can auto-approve content."""
        return (
            self.current_mode == SystemMode.NORMAL 
            and not self.is_paused
        )
    
    def can_auto_post(self) -> bool:
        """Check if system can auto-post content."""
        return (
            self.current_mode == SystemMode.NORMAL 
            and not self.is_paused
        )
    
    def can_generate_content(self) -> bool:
        """Check if system can generate content."""
        return self.current_mode != SystemMode.CRISIS
    
    def get_mode(self) -> SystemMode:
        """Get current system mode."""
        return self.current_mode
    
    def is_manual_mode(self) -> bool:
        """Check if system is in manual mode."""
        return self.current_mode == SystemMode.MANUAL
    
    def is_crisis_mode(self) -> bool:
        """Check if system is in crisis mode."""
        return self.current_mode == SystemMode.CRISIS
    
    async def emergency_shutdown(self, user_id: int):
        """Emergency shutdown (alias for crisis mode)."""
        return await self.execute_action(
            ControlAction.SET_CRISIS,
            user_id,
            "Emergency shutdown initiated"
        )
    
    async def instant_pause(self, user_id: int):
        """Instant pause of all automation."""
        return await self.execute_action(
            ControlAction.PAUSE,
            user_id,
            "Instant pause initiated"
        )
