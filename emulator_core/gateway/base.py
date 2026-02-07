from typing import Dict, Any, Callable
import logging

class BaseGateway:
    """
    Base class for API Gateways.
    Handles dispatching Actions to Backend methods.
    """
    def __init__(self, backend):
        self.backend = backend
        self.actions: Dict[str, Callable] = {}

    def register_action(self, action_name: str, handler: Callable):
        self.actions[action_name] = handler

    def dispatch(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        if action not in self.actions:
            raise Exception(f"InvalidAction: The action {action} is not valid for this web service.")
        
        return self.actions[action](params)
