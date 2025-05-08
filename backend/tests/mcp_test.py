import pytest
import pytest_asyncio
import asyncio
import os
import shutil
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime
import sys
from pathlib import Path

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))
from mcp.mcp import MCP
from mcp.serializer import ContextSerializer
from mcp.pruner import ContextPruner

@pytest_asyncio.fixture
async def mock_serializer():
    serializer = MagicMock(spec=ContextSerializer)
    serializer.serialize = MagicMock(return_value={})
    serializer.deserialize = MagicMock(return_value={
        "userProfile": {
            "preferences": {
                "language": "en",
                "voice_enabled": True,
                "theme": "dark",
                "model_preferences": {
                    "default_model": "llama3",
                    "fallback_model": "gemini"
                }
            },
            "usage_stats": {
                "total_commands": 0,
                "last_active": datetime.now().isoformat(),
                "favorite_commands": []
            }
        },
        "recentCommands": [],
        "activeAgents": [],
        "taskHistory": [],
        "agentStates": {},
        "feedbackLoop": {
            "user_feedback": [],
            "performance_metrics": {},
            "learning_points": []
        },
        "errorLogs": [],
        "compressionLog": {
            "last_compression": None,
            "compression_stats": {},
            "compression_history": []
        },
        "system_state": {
            "last_updated": datetime.now().isoformat(),
            "active_tasks": [],
            "resource_usage": {}
        }
    })
    return serializer

@pytest_asyncio.fixture
async def mock_pruner():
    pruner = MagicMock(spec=ContextPruner)
    pruner.prune = MagicMock(side_effect=lambda x: x)  # Return the same context
    return pruner

@pytest_asyncio.fixture
async def mcp(mock_serializer, mock_pruner):
    # Create a temporary test directory
    test_dir = "tests/tmp"
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    os.makedirs(test_dir)
    
    # Create MCP instance with mocked dependencies
    mcp = MCP(storage_path=test_dir)
    mcp.serializer = mock_serializer
    mcp.pruner = mock_pruner
    
    # Mock file operations
    mcp.save_context = AsyncMock()
    mcp.load_context = AsyncMock()
    
    await mcp.initialize()
    return mcp

@pytest.mark.asyncio
async def test_user_profile_update(mcp):
    # Test valid preference update
    await mcp.update_user_profile("theme", "light")
    user_profile = await mcp.get_user_profile()
    assert user_profile["preferences"]["theme"] == "light"
    
    # Test invalid preference update
    await mcp.update_user_profile("nonexistent_key", "value")
    user_profile = await mcp.get_user_profile()
    assert "nonexistent_key" not in user_profile["preferences"]

@pytest.mark.asyncio
async def test_add_command(mcp):
    # Test adding a command
    await mcp.add_command("test-command", {"status": "ok"})
    assert len(mcp.context["recentCommands"]) == 1
    assert mcp.context["userProfile"]["usage_stats"]["total_commands"] == 1
    
    # Test command with complex result
    complex_result = {"data": [1, 2, 3], "metadata": {"timestamp": datetime.now().isoformat()}}
    await mcp.add_command("complex-command", complex_result)
    assert len(mcp.context["recentCommands"]) == 2
    assert mcp.context["recentCommands"][-1]["result"] == complex_result

@pytest.mark.asyncio
async def test_agent_state_update(mcp):
    # Test basic state update
    await mcp.update_agent_state("agent1", {"mood": "busy"})
    agent_state = await mcp.get_agent_state("agent1")
    assert agent_state["state"]["mood"] == "busy"
    
    # Test updating non-existent agent
    await mcp.update_agent_state("nonexistent_agent", {"status": "active"})
    agent_state = await mcp.get_agent_state("nonexistent_agent")
    assert agent_state["state"]["status"] == "active"

@pytest.mark.asyncio
async def test_feedback_logging(mcp):
    # Test basic feedback
    await mcp.add_feedback("suggestion", "Add more animations")
    feedback = mcp.context["feedbackLoop"]["user_feedback"]
    assert feedback[-1]["content"] == "Add more animations"
    
    # Test feedback with metadata
    metadata = {"priority": "high", "category": "ui"}
    await mcp.add_feedback("bug", "Button not working", metadata)
    feedback = mcp.context["feedbackLoop"]["user_feedback"]
    assert feedback[-1]["metadata"] == metadata

@pytest.mark.asyncio
async def test_error_logging(mcp):
    # Test basic error logging
    try:
        raise ValueError("Oops!")
    except Exception as e:
        await mcp.log_error(e, {"where": "unit test"})
    
    errors = await mcp.get_recent_errors()
    assert errors[-1]["error_type"] == "ValueError"
    assert errors[-1]["context"]["where"] == "unit test"
    
    # Test error log clearing
    await mcp.clear_error_logs()
    errors = await mcp.get_recent_errors()
    assert len(errors) == 0

@pytest.mark.asyncio
async def test_compression_logging(mcp):
    # Test compression stats update
    stats = {"compressed_size": 1000, "original_size": 2000}
    await mcp.update_compression_log(stats)
    compression_stats = await mcp.get_compression_stats()
    assert compression_stats == stats

@pytest.mark.asyncio
async def test_task_history(mcp):
    # Test getting task history
    tasks = await mcp.get_task_history()
    assert isinstance(tasks, list)
    assert len(tasks) == 0  # Initially empty
    
    # Test with limit
    tasks = await mcp.get_task_history(n=5)
    assert len(tasks) == 0  # Still empty but with limit
