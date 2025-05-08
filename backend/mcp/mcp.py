from typing import Dict, List, Any, Optional, Set
from datetime import datetime
import json
from pathlib import Path
import logging
import asyncio
import aiofiles
from .serializer import ContextSerializer
from .pruner import ContextPruner

logger = logging.getLogger(__name__)

class MCP:
    """
    Memory and Context Pruner (MCP) - Central context management system
    Handles state management, pruning, compression, and async context sync
    """
    
    def __init__(self, storage_path: str = "data/mcp"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Core context structure with new schema
        self.context = {
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
            "activeAgents": set(),
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
        }
        
        self.serializer = ContextSerializer()
        self.pruner = ContextPruner()
        self._sync_lock = asyncio.Lock()
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize the MCP instance asynchronously"""
        if not self._initialized:
            await self.load_context()
            self._initialized = True
    
    async def update_user_profile(self, key: str, value: Any) -> None:
        """Update user profile data"""
        async with self._sync_lock:
            if key in self.context["userProfile"]["preferences"]:
                self.context["userProfile"]["preferences"][key] = value
                await self.save_context()
            else:
                logger.warning(f"Attempted to update non-existent preference: {key}")
    
    async def add_command(self, command: str, result: Any) -> None:
        """Add a command to recent history"""
        async with self._sync_lock:
            command_entry = {
                "timestamp": datetime.now().isoformat(),
                "command": command,
                "result": result
            }
            self.context["recentCommands"].append(command_entry)
            self.context["userProfile"]["usage_stats"]["total_commands"] += 1
            self.context["userProfile"]["usage_stats"]["last_active"] = datetime.now().isoformat()
            await self.save_context()
    
    async def update_agent_state(self, agent_id: str, state: Dict[str, Any]) -> None:
        """Update state for a specific agent"""
        async with self._sync_lock:
            self.context["agentStates"][agent_id] = {
                "state": state,
                "last_updated": datetime.now().isoformat()
            }
            await self.save_context()
    
    async def add_feedback(self, feedback_type: str, content: str, metadata: Dict = None) -> None:
        """Add user feedback or performance metrics"""
        async with self._sync_lock:
            feedback_entry = {
                "timestamp": datetime.now().isoformat(),
                "type": feedback_type,
                "content": content,
                "metadata": metadata or {}
            }
            self.context["feedbackLoop"]["user_feedback"].append(feedback_entry)
            await self.save_context()
    
    async def log_error(self, error: Exception, context: Dict = None) -> None:
        """Log an error with context"""
        async with self._sync_lock:
            error_entry = {
                "timestamp": datetime.now().isoformat(),
                "error_type": type(error).__name__,
                "error_message": str(error),
                "context": context or {}
            }
            self.context["errorLogs"].append(error_entry)
            await self.save_context()
    
    async def update_compression_log(self, stats: Dict[str, Any]) -> None:
        """Update compression statistics"""
        async with self._sync_lock:
            self.context["compressionLog"]["last_compression"] = datetime.now().isoformat()
            self.context["compressionLog"]["compression_stats"] = stats
            self.context["compressionLog"]["compression_history"].append({
                "timestamp": datetime.now().isoformat(),
                "stats": stats
            })
            await self.save_context()
    
    async def save_context(self) -> None:
        """Save current context to disk asynchronously"""
        try:
            async with self._sync_lock:
                print("🔒 Acquiring lock to save context")
                # Convert set to list for JSON serialization
                context_to_save = self.context.copy()
                context_to_save["activeAgents"] = list(context_to_save["activeAgents"])
                # Prune context before saving
                pruned_context = self.pruner.prune(context_to_save)
                print("🔧 Pruned. About to serialize")
                # Serialize and save
                serialized = self.serializer.serialize(pruned_context)
                print("📁 Writing to file...")
                async with aiofiles.open(self.storage_path / "context.json", "w") as f:
                    json.dump(serialized, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save context: {e}")
            print("❌ Exception in save_context:", e)
            asyncio.create_task(self.log_error(e, {"operation": "save_context"}))
    
    async def load_context(self) -> None:
        """Load context from disk asynchronously"""
        try:
            async with self._sync_lock:
                context_file = self.storage_path / "context.json"
                if context_file.exists():
                    with open(context_file, "r") as f:
                        serialized = json.load(f)
                    loaded_context = self.serializer.deserialize(serialized)
                    # Convert list back to set for activeAgents
                    loaded_context["activeAgents"] = set(loaded_context["activeAgents"])
                    self.context = loaded_context
        except Exception as e:
            logger.error(f"Failed to load context: {e}")
            await self.log_error(e, {"operation": "load_context"})
    
    async def get_agent_state(self, agent_id: str) -> Optional[Dict]:
        """Get current state for a specific agent"""
        return self.context["agentStates"].get(agent_id)
    
    async def get_recent_errors(self, n: int = 10) -> List[Dict]:
        """Get n most recent errors"""
        return self.context["errorLogs"][-n:]
    
    async def get_compression_stats(self) -> Dict:
        """Get current compression statistics"""
        return self.context["compressionLog"]["compression_stats"]
    
    async def clear_error_logs(self) -> None:
        """Clear error logs"""
        async with self._sync_lock:
            self.context["errorLogs"] = []
            await self.save_context()
    
    async def get_user_profile(self) -> Dict:
        """Get current user profile"""
        return self.context["userProfile"].copy()
    
    async def get_task_history(self, n: int = 10) -> List[Dict]:
        """Get n most recent tasks"""
        return self.context["taskHistory"][-n:]
