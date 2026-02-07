from typing import Dict, Any
from emulator_core.backend import BaseBackend
from emulator_core.state import ErrorCode


class SerialConsoleBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)
        # Initialize serial_console state dict if not present
        if not hasattr(self.state, "serial_console"):
            self.state.serial_console = {}

        # We store a single resource keyed by owner_id, representing the account-wide serial console access status
        owner_id = self.get_owner_id()
        if owner_id not in self.state.serial_console:
            # By default, serial console access is disabled
            self.state.serial_console[owner_id] = {
                "serialConsoleAccessEnabled": False,
                "managedBy": "account",  # default managedBy value
            }

    def _check_dry_run(self, params: Dict[str, Any]) -> None:
        # DryRun parameter is optional boolean
        dry_run = params.get("DryRun")
        if dry_run is not None and not isinstance(dry_run, bool):
            raise ErrorCode("InvalidParameterValue", "DryRun must be a boolean if provided")

        if dry_run:
            # Simulate permission check: always allow for this emulator
            # Raise DryRunOperation error to indicate permission check success
            raise ErrorCode("DryRunOperation", "Request would have succeeded, DryRun flag is set")

    def DisableSerialConsoleAccess(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Disables access to the EC2 serial console of all instances for your account.
        """
        # Validate input parameters
        if not isinstance(params, dict):
            raise ErrorCode("InvalidParameterValue", "Parameters must be a dictionary")

        # Check DryRun
        self._check_dry_run(params)

        # Disable serial console access for this account
        owner_id = self.get_owner_id()
        resource = self.state.serial_console.get(owner_id)
        if resource is None:
            # Initialize if missing
            resource = {
                "serialConsoleAccessEnabled": False,
                "managedBy": "account",
            }
            self.state.serial_console[owner_id] = resource

        resource["serialConsoleAccessEnabled"] = False
        resource["managedBy"] = "account"

        return {
            "requestId": self.generate_request_id(),
            "serialConsoleAccessEnabled": False,
        }

    def EnableSerialConsoleAccess(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enables access to the EC2 serial console of all instances for your account.
        """
        # Validate input parameters
        if not isinstance(params, dict):
            raise ErrorCode("InvalidParameterValue", "Parameters must be a dictionary")

        # Check DryRun
        self._check_dry_run(params)

        # Enable serial console access for this account
        owner_id = self.get_owner_id()
        resource = self.state.serial_console.get(owner_id)
        if resource is None:
            # Initialize if missing
            resource = {
                "serialConsoleAccessEnabled": True,
                "managedBy": "account",
            }
            self.state.serial_console[owner_id] = resource
        else:
            resource["serialConsoleAccessEnabled"] = True
            resource["managedBy"] = "account"

        return {
            "requestId": self.generate_request_id(),
            "serialConsoleAccessEnabled": True,
        }

    def GetSerialConsoleAccessStatus(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Retrieves the access status of your account to the EC2 serial console of all instances.
        """
        # Validate input parameters
        if not isinstance(params, dict):
            raise ErrorCode("InvalidParameterValue", "Parameters must be a dictionary")

        # Check DryRun
        self._check_dry_run(params)

        owner_id = self.get_owner_id()
        resource = self.state.serial_console.get(owner_id)
        if resource is None:
            # Default state if missing
            resource = {
                "serialConsoleAccessEnabled": False,
                "managedBy": "account",
            }
            self.state.serial_console[owner_id] = resource

        # Validate managedBy value
        managed_by = resource.get("managedBy", "account")
        if managed_by not in ("account", "declarative-policy"):
            # Defensive fallback
            managed_by = "account"

        return {
            "managedBy": managed_by,
            "requestId": self.generate_request_id(),
            "serialConsoleAccessEnabled": resource.get("serialConsoleAccessEnabled", False),
        }

from emulator_core.gateway.base import BaseGateway

class SerialconsoleGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("DisableSerialConsoleAccess", self.disable_serial_console_access)
        self.register_action("EnableSerialConsoleAccess", self.enable_serial_console_access)
        self.register_action("GetSerialConsoleAccessStatus", self.get_serial_console_access_status)

    def disable_serial_console_access(self, params):
        return self.backend.disable_serial_console_access(params)

    def enable_serial_console_access(self, params):
        return self.backend.enable_serial_console_access(params)

    def get_serial_console_access_status(self, params):
        return self.backend.get_serial_console_access_status(params)
