from typing import Dict, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class ContextPruner:
    """
    Manages memory usage by pruning old or irrelevant data from context
    Implements various pruning strategies to maintain optimal context size
    """
    
    def __init__(self):
        # Configuration for pruning
        self.max_conversation_history = 100  # Maximum number of conversation messages to keep
        self.max_command_history = 50       # Maximum number of commands to keep
        self.max_age_days = 7               # Maximum age of data to keep (in days)
    
    def prune(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Apply pruning strategies to the context"""
        pruned_context = context.copy()
        
        # Prune conversation history
        if "conversation_history" in pruned_context:
            pruned_context["conversation_history"] = self._prune_conversation_history(
                pruned_context["conversation_history"]
            )
        
        # Prune command history
        if "recent_commands" in pruned_context:
            pruned_context["recent_commands"] = self._prune_command_history(
                pruned_context["recent_commands"]
            )
        
        # Prune system state
        if "system_state" in pruned_context:
            pruned_context["system_state"] = self._prune_system_state(
                pruned_context["system_state"]
            )
        
        return pruned_context
    
    def _prune_conversation_history(self, history: list) -> list:
        """Prune conversation history based on age and size"""
        if not history:
            return []
        
        # Convert timestamps to datetime objects
        now = datetime.now()
        pruned_history = []
        
        for message in history:
            try:
                timestamp = datetime.fromisoformat(message["timestamp"])
                age = now - timestamp
                
                # Keep messages that are newer than max_age_days
                if age <= timedelta(days=self.max_age_days):
                    pruned_history.append(message)
            except (ValueError, KeyError) as e:
                logger.warning(f"Error processing message timestamp: {e}")
                continue
        
        # Keep only the most recent messages up to max_conversation_history
        return pruned_history[-self.max_conversation_history:]
    
    def _prune_command_history(self, commands: list) -> list:
        """Prune command history based on age and size"""
        if not commands:
            return []
        
        # Convert timestamps to datetime objects
        now = datetime.now()
        pruned_commands = []
        
        for command in commands:
            try:
                timestamp = datetime.fromisoformat(command["timestamp"])
                age = now - timestamp
                
                # Keep commands that are newer than max_age_days
                if age <= timedelta(days=self.max_age_days):
                    pruned_commands.append(command)
            except (ValueError, KeyError) as e:
                logger.warning(f"Error processing command timestamp: {e}")
                continue
        
        # Keep only the most recent commands up to max_command_history
        return pruned_commands[-self.max_command_history:]
    
    def _prune_system_state(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Prune system state data"""
        pruned_state = state.copy()
        
        # Update last_updated timestamp
        pruned_state["last_updated"] = datetime.now().isoformat()
        
        # Clear completed tasks
        if "active_tasks" in pruned_state:
            pruned_state["active_tasks"] = [
                task for task in pruned_state["active_tasks"]
                if task.get("status") != "completed"
            ]
        
        # Clear old resource usage data
        if "resource_usage" in pruned_state:
            now = datetime.now()
            pruned_state["resource_usage"] = {
                k: v for k, v in pruned_state["resource_usage"].items()
                if datetime.fromisoformat(k) > (now - timedelta(days=self.max_age_days))
            }
        
        return pruned_state
