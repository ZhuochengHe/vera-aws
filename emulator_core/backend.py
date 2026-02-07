from typing import Dict, Any, List
import uuid
from .state import EmulatorState, ErrorCode

class BaseBackend:
    """
    Base class for all generated service backends.
    Provides access to shared state and common utilities.
    """
    def __init__(self, state: EmulatorState):
        self.state = state

    @property
    def owner_id(self) -> str:
        return "123456789012"

    def generate_id(self, prefix: str) -> str:
        return f"{prefix}-{uuid.uuid4().hex[:8]}"
        
    def generate_unique_id(self, prefix: str = "") -> str:
        """Helper used by generated code"""
        return f"{prefix}{uuid.uuid4().hex[:8]}"

    def generate_request_id(self) -> str:
        """Helper used by generated code"""
        return str(uuid.uuid4())

    def get_owner_id(self) -> str:
        """Helper used by generated code"""
        return "123456789012"

    def fail(self, code: ErrorCode, message: str):
        raise Exception(f"{code.value}: {message}")
