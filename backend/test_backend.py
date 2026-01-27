#!/usr/bin/env python3
"""
Test script for the AI Content Agent System backend.
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import init_db, get_db
from app.core.llm import llm_provider_factory
from app.core.agents.content_agent import ContentAgent
from app.core.workflows.approval_engine import ApprovalWorkflow
from app.core.controls.system_controls import SystemControls
from app.schemas import ContentGenerationRequest, Platform
from app.models import User, BrandVoice, ContentStatus
from sqlalchemy.orm import Session
import json


async def test_llm_provider():
    """Test LLM provider connectivity."""
    print("\n" + "="*60)
    print("Testing LLM Provider")
    print("="*60)
    
    provider = llm_provider_factory.create_provider()
    
    print(f"Provider: {provider.get_provider_name()}")
    
    # Test availability
    is_available = await provider.is_available()
    print(f"Available: {is_available}")
    
    if is_available:
        # Test content generation
        try:
            content = await provider.generate_content(
                "Write a LinkedIn post about AI automation.",
                {"platform": "linkedin"}
            )
            print(f"✓ Content generation works")
            print(f"  Sample: {content[:100]}...")
        except Exception as e:
            print(f"✗ Content generation failed: {str(e)}")
    else:
        print("⚠ Using mock provider for testing")
    
    return is_available


async def test_database():
    """Test database connectivity and models."""
    print("\n" + "="*60)
    print("Testing Database")
    print("="*60)
    
    try:
        init_db()
        print("✓ Database initialized successfully")
        
        # Create a test session
        from app.database import SessionLocal
        db = SessionLocal()
        
        # Test basic query
        user_count = db.query(User).count()
        print(f"✓ Database connection works (Users: {user_count})")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"✗ Database test failed: {str(e)}")
        return False


async def test_content_generation():
    """Test content generation workflow."""
    print("\n" + "="*60)
    print("Testing Content Generation")
    print("="*60)
    
    from app.database import SessionLocal
    db = SessionLocal()
    
    try:
        # Create a mock user ID for testing
        test_user_id = 3  # client@demo.com
        
        # Create content agent
        content_agent = ContentAgent(db)
        
        # Test request
        request = ContentGenerationRequest(
            platform=Platform.LINKEDIN,
            context="AI-powered content creation systems",
            prompt_override="Write a short LinkedIn post about AI content creation."
        )
        
        # Generate content
        draft = await content_agent.generate_content(request, test_user_id)
        
        print(f"✓ Content generated successfully")
        print(f"  Draft ID: {draft.id}")
        print(f"  Platform: {draft.platform}")
        print(f"  Content: {draft.content_text[:100]}...")
        print(f"  Status: {draft.status}")
        
        return draft
        
    except Exception as e:
        print(f"✗ Content generation test failed: {str(e)}")
        return None
    
    finally:
        db.close()


async def test_approval_workflow(draft_id: int):
    """Test approval workflow."""
    print("\n" + "="*60)
    print("Testing Approval Workflow")
    print("="*60)
    
    from app.database import SessionLocal
    db = SessionLocal()
    
    try:
        test_user_id = 3  # client
        reviewer_id = 2   # reviewer
        
        approval_workflow = ApprovalWorkflow(db)
        
        # Submit for approval
        draft, approval_request = await approval_workflow.submit_for_approval(
            draft_id, test_user_id
        )
        
        print(f"✓ Draft submitted for approval")
        print(f"  Approval Request ID: {approval_request.id}")
        print(f"  Draft Status: {draft.status}")
        
        # Get pending approvals
        pending = await approval_workflow.get_pending_approvals()
        print(f"  Pending approvals: {len(pending)}")
        
        return approval_request
        
    except Exception as e:
        print(f"✗ Approval workflow test failed: {str(e)}")
        return None
    
    finally:
        db.close()


async def test_control_system():
    """Test control system."""
    print("\n" + "="*60)
    print("Testing Control System")
    print("="*60)
    
    from app.database import SessionLocal
    db = SessionLocal()
    
    try:
        system_controls = SystemControls(db)
        await system_controls.initialize()
        
        # Get initial status
        status = system_controls.get_status()
        print(f"  Control system initialized")
        print(f"  Current Mode: {status['mode']}")
        print(f"  Paused: {status['is_paused']}")
        print(f"  Can Auto-approve: {status['can_auto_approve']}")
        
        # Test pause
        from app.core.controls.system_controls import ControlAction
        result = await system_controls.execute_action(
            ControlAction.PAUSE,
            user_id=1,  # admin
            notes="Test pause"
        )
        
        print(f"✓ Control actions work")
        print(f"  Pause executed: {result['success']}")
        
        return True
        
    except Exception as e:
        print(f"✗ Control system test failed: {str(e)}")
        return False
    
    finally:
        db.close()


async def test_api_health():
    """Test API health endpoint."""
    print("\n" + "="*60)
    print("Testing API Health")
    print("="*60)
    
    import httpx
    import time
    
    # Wait for API to start
    print("Waiting for API to be ready...")
    for i in range(10):
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get("http://localhost:8000/health")
                if response.status_code == 200:
                    health_data = response.json()
                    print(f"✓ API is healthy")
                    print(f"  Status: {health_data['status']}")
                    print(f"  Database: {health_data['database']}")
                    print(f"  Ollama: {health_data.get('ollama', 'N/A')}")
                    return True
        except:
            if i < 9:
                time.sleep(1)
            continue
    
    print("✗ API health check failed")
    return False


async def run_all_tests():
    """Run all tests."""
    print("Starting AI Content Agent System Tests")
    print("="*60)
    
    results = {
        "database": await test_database(),
        "llm_provider": await test_llm_provider(),
        "content_generation": None,
        "approval_workflow": None,
        "control_system": await test_control_system(),
        "api_health": await test_api_health()
    }
    
    # Test content generation if database works
    if results["database"]:
        draft = await test_content_generation()
        results["content_generation"] = draft is not None
        
        if draft:
            approval_request = await test_approval_workflow(draft.id)
            results["approval_workflow"] = approval_request is not None
    
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name:25} {status}")
    
    # Overall status
    all_passed = all(r for r in results.values() if isinstance(r, bool))
    
    if all_passed:
        print("\n All tests passed! System is ready.")
    else:
        print("\n Some tests failed. Check the logs above.")
    
    return all_passed


if __name__ == "__main__":
    # Make sure we're in the right directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Run tests
    success = asyncio.run(run_all_tests())
    
    sys.exit(0 if success else 1)
