import re
from typing import Dict, List, Optional, Tuple
from .utils import setup_logger

logger = setup_logger(__name__)

class CommandParser:
    def __init__(self):
        self.commands: Dict[str, List[str]] = {
            "wake": ["aura", "hey aura", "wake up"],
            "stop": ["stop", "pause", "halt"],
            "help": ["help", "what can you do", "commands"],
            "status": ["status", "are you there", "are you listening"],
        }
        
        # Compile regex patterns for faster matching
        self.patterns = {
            cmd: [re.compile(pattern, re.IGNORECASE) 
                 for pattern in patterns]
            for cmd, patterns in self.commands.items()
        }

    def parse_command(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Parse text for commands and return command type and remaining text
        
        Args:
            text: Input text to parse
            
        Returns:
            Tuple[Optional[str], Optional[str]]: (command_type, remaining_text)
        """
        text = text.lower().strip()
        
        # Check for wake word first
        if any(pattern.match(text) for pattern in self.patterns["wake"]):
            return "wake", text
            
        # Check other commands
        for cmd_type, patterns in self.patterns.items():
            for pattern in patterns:
                match = pattern.search(text)
                if match:
                    # Remove the command from text
                    remaining = text[:match.start()] + text[match.end():]
                    remaining = remaining.strip()
                    return cmd_type, remaining
                    
        return None, text

    def is_wake_word(self, text: str) -> bool:
        """Check if text contains wake word"""
        text = text.lower().strip()
        return any(pattern.match(text) for pattern in self.patterns["wake"])

    def get_command_help(self) -> str:
        """Return help text for available commands"""
        help_text = "Available commands:\n"
        for cmd, patterns in self.commands.items():
            help_text += f"- {cmd}: {', '.join(patterns)}\n"
        return help_text 