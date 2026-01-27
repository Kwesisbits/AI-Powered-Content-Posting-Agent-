"""
Control system API endpoints.
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import SystemStatusResponse, ControlAction
from app.api.v1.endpoints.auth import get_current_user
from app.core.controls.system_controls import SystemControls, ControlAction as SysControlAction

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/status", response_model=SystemStatusResponse)
async def get_system_status(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current system status and controls."""
    system_controls = SystemControls(db)
    await system_controls.initialize()
    
    status_data = system_controls.get_status()
    
    return SystemStatusResponse(
        mode=status_data["mode"],
        is_paused=status_data["is_paused"],
        last_updated_at=datetime.fromisoformat(status_data["last_updated"]) if status_data["last_updated"] else None,
        notes="System operational"
    )


@router.post("/pause")
async def pause_system(
    action: ControlAction,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Control system actions (pause, resume, mode changes)."""
    
    # Map API action to system control action
    action_map = {
        "pause": SysControlAction.PAUSE,
        "resume": SysControlAction.RESUME,
        "set_manual": SysControlAction.SET_MANUAL,
        "set_crisis": SysControlAction.SET_CRISIS,
        "set_normal": SysControlAction.SET_NORMAL
    }
    
    if action.action not in action_map:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid action: {action.action}"
        )
    
    # Only admins can change system controls
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can change system controls"
        )
    
    system_controls = SystemControls(db)
    await system_controls.initialize()
    
    try:
        result = await system_controls.execute_action(
            action_map[action.action],
            current_user.id,
            action.notes
        )
        
        return {
            "success": True,
            "message": f"System {action.action} executed successfully",
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Control action failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Control action failed: {str(e)}"
        )


@router.post("/emergency-pause")
async def emergency_pause(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Emergency pause - instant halt of all automation."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can execute emergency actions"
        )
    
    system_controls = SystemControls(db)
    await system_controls.initialize()
    
    result = await system_controls.instant_pause(current_user.id)
    
    return {
        "success": True,
        "message": "Emergency pause executed. All automation halted.",
        "result": result
    }


@router.post("/crisis-mode")
async def crisis_mode(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Activate crisis mode - emergency shutdown."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can activate crisis mode"
        )
    
    system_controls = SystemControls(db)
    await system_controls.initialize()
    
    result = await system_controls.emergency_shutdown(current_user.id)
    
    return {
        "success": True,
        "message": "CRISIS MODE ACTIVATED. Emergency shutdown initiated.",
        "result": result
    }
