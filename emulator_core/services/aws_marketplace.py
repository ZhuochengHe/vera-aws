from typing import Dict, Any
from emulator_core.backend import BaseBackend
from emulator_core.state import ErrorCode


class AwsMarketplaceBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)
        # Use self.state.aws_marketplace dict for storage if needed
        # But this API does not create resources, so no storage needed here

    def confirm_product_instance(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Validate required parameters
        if "InstanceId" not in params:
            raise ErrorCode("MissingParameter", "InstanceId is required")
        if "ProductCode" not in params:
            raise ErrorCode("MissingParameter", "ProductCode is required")

        instance_id = params["InstanceId"]
        product_code = params["ProductCode"]
        dry_run = params.get("DryRun", False)

        # Validate types
        if not isinstance(instance_id, str) or not instance_id:
            raise ErrorCode("InvalidParameterValue", "InstanceId must be a non-empty string")
        if not isinstance(product_code, str) or not product_code:
            raise ErrorCode("InvalidParameterValue", "ProductCode must be a non-empty string")
        if not isinstance(dry_run, bool):
            raise ErrorCode("InvalidParameterValue", "DryRun must be a boolean")

        # DryRun check
        if dry_run:
            # Check permissions - simplified: assume permission granted
            # Raise DryRunOperation error if permissions are OK
            raise ErrorCode("DryRunOperation", "Request would have succeeded, but DryRun flag is set")

        # Validate instance exists
        instance = self.state.get_resource(instance_id)
        if instance is None:
            raise ErrorCode("InvalidInstanceID.NotFound", f"The instance ID '{instance_id}' does not exist")

        # Validate product code ownership
        # The product code must be owned by the caller (owner of product code)
        # We assume instance has attribute 'product_codes' which is a list of product code strings
        # And product code ownership is checked by comparing with self.get_owner_id()
        owner_id = self.get_owner_id()

        # Check if product_code is owned by caller
        # For this emulation, assume product codes owned by caller are stored in self.state.aws_marketplace['owned_product_codes']
        owned_product_codes = self.state.aws_marketplace.get("owned_product_codes", set())
        if product_code not in owned_product_codes:
            raise ErrorCode("UnauthorizedOperation", "You do not own the specified product code")

        # Check if product code is associated with the instance
        # Assume instance has attribute 'product_codes' which is a list or set of product codes attached to it
        instance_product_codes = getattr(instance, "product_codes", set())
        if not isinstance(instance_product_codes, (set, list)):
            instance_product_codes = set()
        else:
            instance_product_codes = set(instance_product_codes)

        is_associated = product_code in instance_product_codes

        # Return response
        return {
            "ownerId": owner_id if is_associated else None,
            "requestId": self.generate_request_id(),
            "return": is_associated,
        }

from emulator_core.gateway.base import BaseGateway

class AWSMarketplaceGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("ConfirmProductInstance", self.confirm_product_instance)

    def confirm_product_instance(self, params):
        return self.backend.confirm_product_instance(params)
