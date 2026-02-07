from typing import Dict, Any
from emulator_core.backend import BaseBackend
from emulator_core.state import ErrorCode


class NitroTpmBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)
        # Use self.state.nitro_tpm as dict storage for Nitro TPM resources

    def GetInstanceTpmEkPub(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Validate required parameters
        if not isinstance(params, dict):
            raise ErrorCode("InvalidParameter", "Parameters must be a dictionary")

        # DryRun is optional boolean
        dry_run = params.get("DryRun")
        if dry_run is not None and not isinstance(dry_run, bool):
            raise ErrorCode("InvalidParameterValue", "DryRun must be a boolean if specified")

        # InstanceId required string
        instance_id = params.get("InstanceId")
        if not instance_id or not isinstance(instance_id, str):
            raise ErrorCode("MissingParameter", "InstanceId is required and must be a string")

        # KeyFormat required string, must be one of "der", "tpmt"
        key_format = params.get("KeyFormat")
        if not key_format or not isinstance(key_format, str):
            raise ErrorCode("MissingParameter", "KeyFormat is required and must be a string")
        key_format_lower = key_format.lower()
        if key_format_lower not in ("der", "tpmt"):
            raise ErrorCode("InvalidParameterValue", "KeyFormat must be one of 'der' or 'tpmt'")

        # KeyType required string, must be one of "rsa-2048", "ecc-sec-p384"
        key_type = params.get("KeyType")
        if not key_type or not isinstance(key_type, str):
            raise ErrorCode("MissingParameter", "KeyType is required and must be a string")
        key_type_lower = key_type.lower()
        if key_type_lower not in ("rsa-2048", "ecc-sec-p384"):
            raise ErrorCode("InvalidParameterValue", "KeyType must be one of 'rsa-2048' or 'ecc-sec-p384'")

        # Validate instance exists by cross-resource access
        instance = self.state.get_resource(instance_id)
        if instance is None:
            # According to AWS behavior, if DryRun is True, raise UnauthorizedOperation
            if dry_run:
                raise ErrorCode("UnauthorizedOperation", "You are not authorized to perform this operation.")
            raise ErrorCode("InvalidInstanceID.NotFound", f"The instance ID '{instance_id}' does not exist")

        # If DryRun is True, simulate permission check success
        if dry_run:
            raise ErrorCode("DryRunOperation", "Request would have succeeded, but DryRun flag is set")

        # Generate a dummy public endorsement key material
        # For emulation, we can generate a base64 string depending on key_format and key_type
        # In real AWS, this is a base64-encoded public key in the requested format

        # For simplicity, create a fake key value string
        # Format: base64("NitroTPM-{instance_id}-{key_format}-{key_type}")
        import base64

        raw_key = f"NitroTPM-{instance_id}-{key_format_lower}-{key_type_lower}".encode("utf-8")
        key_value = base64.b64encode(raw_key).decode("utf-8")

        # Compose response
        response = {
            "instanceId": instance_id,
            "keyFormat": key_format_lower,
            "keyType": key_type_lower,
            "keyValue": key_value,
            "requestId": self.generate_request_id(),
        }

        return response

from emulator_core.gateway.base import BaseGateway

class NitroTPMGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("GetInstanceTpmEkPub", self.get_instance_tpm_ek_pub)

    def get_instance_tpm_ek_pub(self, params):
        return self.backend.get_instance_tpm_ek_pub(params)
