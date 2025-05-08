from typing import Any, Dict
from datetime import datetime
import json

class ContextSerializer:
    """
    Handles serialization and deserialization of context data
    Converts complex Python objects to JSON-serializable format
    """
    
    def serialize(self, data: Any) -> Dict:
        """Convert complex Python objects to JSON-serializable format"""
        if isinstance(data, dict):
            return {k: self.serialize(v) for k, v in data.items()}
        elif isinstance(data, (list, tuple)):
            return [self.serialize(item) for item in data]
        elif isinstance(data, datetime):
            return {
                "__type__": "datetime",
                "value": data.isoformat()
            }
        elif isinstance(data, set):
            return {
                "__type__": "set",
                "value": list(data)
            }
        return data
    
    def deserialize(self, data: Any) -> Any:
        """Convert serialized data back to Python objects"""
        if isinstance(data, dict):
            if "__type__" in data:
                if data["__type__"] == "datetime":
                    return datetime.fromisoformat(data["value"])
                elif data["__type__"] == "set":
                    return set(data["value"])
            return {k: self.deserialize(v) for k, v in data.items()}
        elif isinstance(data, (list, tuple)):
            return [self.deserialize(item) for item in data]
        return data
